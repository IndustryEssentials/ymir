from collections import defaultdict
import enum
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from google.protobuf.json_format import ParseDict
import xmltodict
import yaml

from mir.tools import class_ids, mir_storage_ops
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.revs_parser import TypRevTid
from mir.tools.settings import COCO_JSON_NAME
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb


class UnknownTypesStrategy(str, enum.Enum):
    STOP = 'stop'
    IGNORE = 'ignore'
    ADD = 'add'


class MergeStrategy(str, enum.Enum):
    STOP = 'stop'
    HOST = 'host'
    GUEST = 'guest'


def parse_anno_format(anno_format_str: str) -> "mirpb.ExportFormat.V":
    _anno_dict: Dict[str, mirpb.ExportFormat.V] = {
        # compatible with legacy format.
        "voc": mirpb.ExportFormat.EF_VOC_XML,
        "ark": mirpb.ExportFormat.EF_ARK_TXT,
        "ls_json": mirpb.ExportFormat.EF_LS_JSON,
        "det-voc": mirpb.ExportFormat.EF_VOC_XML,
        "det-ark": mirpb.ExportFormat.EF_ARK_TXT,
        "det-ls-json": mirpb.ExportFormat.EF_LS_JSON,
        "seg-coco": mirpb.ExportFormat.EF_COCO_JSON,
    }
    return _anno_dict.get(anno_format_str.lower(), mirpb.ExportFormat.EF_NO_ANNOTATIONS)


def parse_anno_type(anno_type_str: str) -> "mirpb.ObjectType.V":
    _anno_dict: Dict[str, mirpb.ObjectType.V] = {
        "det-box": mirpb.ObjectType.OT_DET_BOX,
        "seg": mirpb.ObjectType.OT_SEG,
    }
    return _anno_dict.get(anno_type_str.lower(), mirpb.ObjectType.OT_UNKNOWN)


def _annotation_parse_func(anno_type: "mirpb.ObjectType.V") -> Callable:
    _func_dict: Dict["mirpb.ObjectType.V", Callable] = {
        mirpb.ObjectType.OT_DET_BOX: _import_annotations_voc_xml,
        mirpb.ObjectType.OT_SEG: import_annotations_coco_json,
    }
    if anno_type not in _func_dict:
        raise NotImplementedError()
    return _func_dict[anno_type]


def _voc_object_dict_to_annotation(object_dict: dict, cid: int) -> mirpb.ObjectAnnotation:
    # Fill shared fields.
    annotation = mirpb.ObjectAnnotation()
    annotation.class_id = cid
    annotation.score = float(object_dict.get('confidence', '-1.0'))
    annotation.anno_quality = float(object_dict.get('box_quality', '-1.0'))
    tags = object_dict.get('tags', {})  # tags could be None
    if tags:
        annotation.tags.update(tags)

    if object_dict.get('bndbox'):
        bndbox_dict: Dict[str, Any] = object_dict['bndbox']
        xmin = int(float(bndbox_dict['xmin']))
        ymin = int(float(bndbox_dict['ymin']))
        xmax = int(float(bndbox_dict['xmax']))
        ymax = int(float(bndbox_dict['ymax']))
        width = xmax - xmin + 1
        height = ymax - ymin + 1

        annotation.box.x = xmin
        annotation.box.y = ymin
        annotation.box.w = width
        annotation.box.h = height
        annotation.box.rotate_angle = float(bndbox_dict.get('rotate_angle', '0.0'))
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no value for bndbox')
    return annotation


def _coco_object_dict_to_annotation(anno_dict: dict, category_id_to_cids: Dict[int, int],
                                    class_type_manager: class_ids.UserLabels) -> Optional[mirpb.ObjectAnnotation]:
    if 'bbox' not in anno_dict or len(anno_dict['bbox']) != 4:
        return None

    obj_anno = mirpb.ObjectAnnotation()

    # box, polygon and mask
    seg_obj = anno_dict.get('segmentation')
    if isinstance(seg_obj, dict):  # mask
        obj_anno.type = mirpb.ObjectType.OT_SEG_MASK
        obj_anno.mask = seg_obj['counts']
    elif isinstance(seg_obj, list):  # polygon
        if len(seg_obj) > 1:
            raise NotImplementedError('Multi polygons not supported')

        obj_anno.type = mirpb.ObjectType.OT_SEG_POLYGON
        points_list = seg_obj[0]
        for i in range(0, len(points_list), 2):
            obj_anno.polygon.append(mirpb.IntPoint(x=int(points_list[i]), y=int(points_list[i + 1]), z=0))
    else:
        obj_anno.type = mirpb.ObjectType.OT_DET_BOX

    bbox_list = anno_dict['bbox']
    obj_anno.box.x = int(bbox_list[0])
    obj_anno.box.y = int(bbox_list[1])
    obj_anno.box.w = int(bbox_list[2])
    obj_anno.box.h = int(bbox_list[3])

    obj_anno.iscrowd = anno_dict.get('iscrowd', 0)
    obj_anno.class_id = category_id_to_cids[anno_dict['category_id']]
    obj_anno.class_name = class_type_manager.main_name_for_id(obj_anno.class_id)

    # ymir defined
    obj_anno.cm = mirpb.ConfusionMatrixType.NotSet
    obj_anno.det_link_id = -1
    obj_anno.score = float(anno_dict.get('confidence', '-1.0'))
    obj_anno.anno_quality = float(anno_dict.get('box_quality', '-1.0'))

    return obj_anno


def import_annotations(mir_annotation: mirpb.MirAnnotations, label_storage_file: str, prediction_dir_path: str,
                       groundtruth_dir_path: str, file_name_to_asset_ids: Dict[str, str],
                       unknown_types_strategy: UnknownTypesStrategy, anno_type: "mirpb.ObjectType.V",
                       phase: str) -> Dict[str, int]:
    anno_import_result: Dict[str, int] = defaultdict(int)

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.load_or_create_userlabels(label_storage_file=label_storage_file)
    logging.info("loaded type id and names: %d", len(class_type_manager.all_ids()))

    if prediction_dir_path:
        logging.info(f"wrting prediction in {prediction_dir_path}")
        _import_annotations_from_dir(
            file_name_to_asset_ids=file_name_to_asset_ids,
            mir_annotation=mir_annotation,
            annotations_dir_path=prediction_dir_path,
            class_type_manager=class_type_manager,
            unknown_types_strategy=unknown_types_strategy,
            accu_new_class_names=anno_import_result,
            image_annotations=mir_annotation.prediction,
            anno_type=anno_type,
        )
        _import_annotation_meta(class_type_manager=class_type_manager,
                                annotations_dir_path=prediction_dir_path,
                                task_annotations=mir_annotation.prediction)
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=0.5)

    if groundtruth_dir_path:
        logging.info(f"wrting ground-truth in {groundtruth_dir_path}")
        _import_annotations_from_dir(
            file_name_to_asset_ids=file_name_to_asset_ids,
            mir_annotation=mir_annotation,
            annotations_dir_path=groundtruth_dir_path,
            class_type_manager=class_type_manager,
            unknown_types_strategy=unknown_types_strategy,
            accu_new_class_names=anno_import_result,
            image_annotations=mir_annotation.ground_truth,
            anno_type=anno_type,
        )
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=1.0)

    if unknown_types_strategy == UnknownTypesStrategy.STOP and anno_import_result:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_UNKNOWN_TYPES,
                              error_message=f"{list(anno_import_result.keys())}")

    return anno_import_result


def _import_annotations_from_dir(file_name_to_asset_ids: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                 annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                 unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                 image_annotations: mirpb.SingleTaskAnnotations,
                                 anno_type: "mirpb.ObjectType.V") -> None:
    image_annotations.type = anno_type
    _annotation_parse_func(anno_type)(
        file_name_to_asset_ids=file_name_to_asset_ids,
        mir_annotation=mir_annotation,
        annotations_dir_path=annotations_dir_path,
        class_type_manager=class_type_manager,
        unknown_types_strategy=unknown_types_strategy,
        accu_new_class_names=accu_new_class_names,
        image_annotations=image_annotations,
    )

    logging.warning(f"imported {len(image_annotations.image_annotations)} / {len(file_name_to_asset_ids)} annotations")


def _import_annotations_voc_xml(file_name_to_asset_ids: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                image_annotations: mirpb.SingleTaskAnnotations) -> None:
    add_if_not_found = (unknown_types_strategy == UnknownTypesStrategy.ADD)
    for filename, asset_hash in file_name_to_asset_ids.items():
        # for each asset, import it's annotations
        annotation_file = os.path.join(annotations_dir_path, os.path.splitext(filename)[0] + '.xml')
        if not os.path.isfile(annotation_file):
            continue

        with open(annotation_file, 'r') as f:
            annos_xml_str = f.read()
        if not annos_xml_str:
            logging.error(f"cannot open annotation_file: {annotation_file}")
            continue

        annos_dict: dict = xmltodict.parse(annos_xml_str)['annotation']
        # cks
        cks = annos_dict.get('cks', {})  # cks could be None
        if cks:
            mir_annotation.image_cks[asset_hash].cks.update(cks)
        mir_annotation.image_cks[asset_hash].image_quality = float(annos_dict.get('image_quality', '-1.0'))

        # annotations and tags
        objects: Union[List[dict], dict] = annos_dict.get('object', [])
        if isinstance(objects, dict):
            # when there's only ONE object node in xml, it will be parsed to a dict, not a list
            objects = [objects]

        anno_idx = 0
        for object_dict in objects:
            cid, new_type_name = class_type_manager.id_and_main_name_for_name(name=object_dict['name'])

            # check if seen this class_name.
            if new_type_name in accu_new_class_names:
                accu_new_class_names[new_type_name] += 1
            else:
                # for unseen class_name, only care about negative cid.
                if cid < 0:
                    if add_if_not_found:
                        cid, _ = class_type_manager.add_main_name(main_name=new_type_name)
                    accu_new_class_names[new_type_name] = 0

            if cid >= 0:
                annotation = _voc_object_dict_to_annotation(object_dict, cid)
                annotation.index = anno_idx
                image_annotations.image_annotations[asset_hash].boxes.append(annotation)
                anno_idx += 1


def import_annotations_coco_json(file_name_to_asset_ids: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                 annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                 unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                 image_annotations: mirpb.SingleTaskAnnotations,
                                 coco_json_filename: str = COCO_JSON_NAME) -> None:
    add_if_not_found = (unknown_types_strategy == UnknownTypesStrategy.ADD)

    coco_file_path = os.path.join(annotations_dir_path, coco_json_filename)
    with open(coco_file_path, 'r') as f:
        coco_obj = json.loads(f.read())
        images_list = coco_obj['images']
        categories_list = coco_obj['categories']
        annotations_list = coco_obj['annotations']

    if not images_list or not isinstance(images_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find images list in coco json: {coco_file_path}")
    if not isinstance(categories_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find categories list in coco json: {coco_file_path}")
    if not isinstance(annotations_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find annotations list in coco json: {coco_file_path}")

    unhashed_filenames_cnt = 0
    unknown_category_ids_cnt = 0
    unknown_image_objects_cnt = 0
    error_format_objects_cnt = 0

    # images_list -> image_id_to_hashes (key: coco image id, value: ymir asset hash)
    image_id_to_hashes: Dict[int, str] = {}
    for v in images_list:
        filename = v['file_name']
        if filename not in file_name_to_asset_ids:
            unhashed_filenames_cnt += 1
            continue
        image_id_to_hashes[v['id']] = file_name_to_asset_ids[filename]

    # categories_list -> category_id_to_cids (key: coco category id, value: ymir class id)
    category_id_to_cids: Dict[int, int] = {}
    for v in categories_list:
        name = v['name']
        cid, _ = class_type_manager.id_and_main_name_for_name(name)
        if cid >= 0:
            category_id_to_cids[v['id']] = cid
        else:
            accu_new_class_names[name] = 0
            if add_if_not_found:
                cid, _ = class_type_manager.add_main_name(name)
                category_id_to_cids[v['id']] = cid

    for anno_dict in annotations_list:
        if anno_dict['category_id'] not in category_id_to_cids:
            unknown_category_ids_cnt += 1
            continue
        if anno_dict['image_id'] not in image_id_to_hashes:
            unknown_image_objects_cnt += 1
            continue

        obj_anno = _coco_object_dict_to_annotation(anno_dict=anno_dict,
                                                   category_id_to_cids=category_id_to_cids,
                                                   class_type_manager=class_type_manager)
        if not obj_anno:
            error_format_objects_cnt += 1
            continue
        asset_hash = image_id_to_hashes[anno_dict['image_id']]
        obj_anno.index = len(image_annotations.image_annotations[asset_hash].boxes)
        image_annotations.image_annotations[asset_hash].boxes.append(obj_anno)

    logging.info(f"count of unhashed file names in images list: {unhashed_filenames_cnt}")
    logging.info(f"count of unknown category ids in categories list: {unknown_category_ids_cnt}")
    logging.info(f"count of objects with unknown image ids in annotations list: {unknown_image_objects_cnt}")
    logging.info(f"count of error format objects: {error_format_objects_cnt}")


def _import_annotation_meta(class_type_manager: class_ids.UserLabels, annotations_dir_path: str,
                            task_annotations: mirpb.SingleTaskAnnotations) -> None:
    annotation_meta_path = os.path.join(annotations_dir_path, 'meta.yaml')
    if not os.path.isfile(annotation_meta_path):
        return

    try:
        with open(annotation_meta_path, 'r') as f:
            annotation_meta_dict = yaml.safe_load(f)
    except Exception:
        annotation_meta_dict = None
    if not isinstance(annotation_meta_dict, dict):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_META_YAML_FILE,
                              error_message='Invalid meta.yaml')

    # model
    if 'model' in annotation_meta_dict:
        ParseDict(annotation_meta_dict['model'], task_annotations.model)

    # eval_class_ids
    eval_class_names = annotation_meta_dict.get('eval_class_names') or task_annotations.model.class_names
    task_annotations.eval_class_ids[:] = set(
        class_type_manager.id_for_names(list(eval_class_names), drop_unknown_names=True)[0])

    # executor_config
    if 'executor_config' in annotation_meta_dict:
        task_annotations.executor_config = json.dumps(annotation_meta_dict['executor_config'])


def copy_annotations_pred_meta(src_task_annotations: mirpb.SingleTaskAnnotations,
                               dst_task_annotations: mirpb.SingleTaskAnnotations) -> None:
    dst_task_annotations.eval_class_ids[:] = src_task_annotations.eval_class_ids
    dst_task_annotations.executor_config = src_task_annotations.executor_config
    dst_task_annotations.model.CopyFrom(src_task_annotations.model)


# copy
def map_and_filter_annotations(mir_annotations: mirpb.MirAnnotations, data_label_storage_file: str,
                               label_storage_file: str) -> List[str]:
    """
    re-map and filter class ids for ground truth and prediction

    Args:
        mir_annotations (mirpb.MirAnnotations): in/out, pred and gt to be updated
        data_label_storage_file (str): in, source label storage file
        label_storage_file (str): in, dest label storage file

    Returns:
        List[str]: unknown class names
    """
    if (data_label_storage_file == label_storage_file
            or (len(mir_annotations.prediction.image_annotations) == 0
                and len(mir_annotations.ground_truth.image_annotations) == 0)):
        # no need to make any changes to annotations
        return []

    src_class_id_mgr = class_ids.load_or_create_userlabels(label_storage_file=data_label_storage_file)
    dst_class_id_mgr = class_ids.load_or_create_userlabels(label_storage_file=label_storage_file)

    cids_mapping = {
        src_class_id_mgr.id_and_main_name_for_name(n)[0]: dst_class_id_mgr.id_and_main_name_for_name(n)[0]
        for n in src_class_id_mgr.all_main_names()
    }
    known_cids_mapping = {k: v for k, v in cids_mapping.items() if v >= 0}

    for sia in mir_annotations.prediction.image_annotations.values():
        for oa in sia.boxes:
            if oa.class_id in known_cids_mapping:
                oa.class_id = known_cids_mapping[oa.class_id]
            else:
                sia.boxes.remove(oa)
    for sia in mir_annotations.ground_truth.image_annotations.values():
        for oa in sia.boxes:
            if oa.class_id in known_cids_mapping:
                oa.class_id = known_cids_mapping[oa.class_id]
            else:
                sia.boxes.remove(oa)

    mir_annotations.prediction.eval_class_ids[:] = [
        known_cids_mapping[cid] for cid in mir_annotations.prediction.eval_class_ids if cid in known_cids_mapping
    ]

    return src_class_id_mgr.main_name_for_ids(list(cids_mapping.keys() - known_cids_mapping.keys()))


# filter and sampling
def filter_mirdatas_by_asset_ids(
        asset_ids_set: Set[str],
        mir_metadatas: mirpb.MirMetadatas = mirpb.MirMetadatas(),
        mir_annotations: mirpb.MirAnnotations = mirpb.MirAnnotations(),
) -> None:
    """
    filter mir_annotations by asset_ids_set in place

    Args:
        mir_metadatas (mirpb.MirMetadatas), in/out: assets to be filtered
        mir_annotations (mirpb.MirAnnotations), in/out: pred and gt to be filtered
        asset_ids_set (Set[str]), in: asset ids
    """
    for asset_id in mir_metadatas.attributes.keys() - asset_ids_set:
        del mir_metadatas.attributes[asset_id]
    for asset_id in mir_annotations.ground_truth.image_annotations.keys() - asset_ids_set:
        del mir_annotations.ground_truth.image_annotations[asset_id]
    for asset_id in mir_annotations.prediction.image_annotations.keys() - asset_ids_set:
        del mir_annotations.prediction.image_annotations[asset_id]
    for asset_id in mir_annotations.image_cks.keys() - asset_ids_set:
        del mir_annotations.image_cks[asset_id]


# merge
def tvt_type_from_str(typ: str) -> 'mirpb.TvtType.V':
    mapping = {
        'tr': mirpb.TvtType.TvtTypeTraining,
        'va': mirpb.TvtType.TvtTypeValidation,
        'te': mirpb.TvtType.TvtTypeTest,
    }
    return mapping.get(typ.lower(), mirpb.TvtType.TvtTypeUnknown)


def merge_to_mirdatas(host_mir_metadatas: mirpb.MirMetadatas, host_mir_annotations: mirpb.MirAnnotations, mir_root: str,
                      guest_typ_rev_tid: TypRevTid, strategy: MergeStrategy) -> None:
    """
    merge contents in `guest_typ_rev_tid` to host mir datas

    Args:
        host_mir_metadatas (mirpb.MirMetadatas): host metadatas
        host_mir_annotations (mirpb.MirAnnotations): host annotations
        mir_root (str): path to mir repo
        guest_typ_rev_tid (revs_parser.TypRevTid): guest typ:rev@tid
        strategy (str): host / guest / stop

    Raises:
        RuntimeError: when guest branch has no metadatas
    """
    guest_mir_metadatas: mirpb.MirMetadatas
    guest_mir_annotations: mirpb.MirAnnotations
    guest_mir_metadatas, guest_mir_annotations = mir_storage_ops.MirStorageOps.load_multiple_storages(
        mir_root=mir_root,
        mir_branch=guest_typ_rev_tid.rev,
        mir_task_id=guest_typ_rev_tid.tid,
        ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS],
        as_dict=False)

    if not guest_mir_metadatas.attributes:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                              error_message=f"guest repo {mir_root}:{guest_typ_rev_tid.rev} has no metadata.")

    id_host_only, id_guest_only, id_joint = match_asset_ids(set(host_mir_metadatas.attributes.keys()),
                                                            set(guest_mir_metadatas.attributes.keys()))

    logging.info(f"{guest_typ_rev_tid} host assets: {len(id_host_only)}, guest assets: {len(id_guest_only)}, "
                 f"joint assets: {len(id_joint)}")

    if strategy == MergeStrategy.STOP and id_joint:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_MERGE_ERROR,
                              error_message='Found conflict on merge strategy STOP: abort')

    _merge_metadatas(host_mir_metadatas=host_mir_metadatas,
                     guest_mir_metadatas=guest_mir_metadatas,
                     id_guest_only=id_guest_only,
                     id_joint=id_joint,
                     suggested_tvt_type=tvt_type_from_str(guest_typ_rev_tid.typ),
                     strategy=strategy)

    if not guest_mir_annotations:
        logging.warning("guest repo {}:{} has no annotations.".format(mir_root, guest_typ_rev_tid.rev))
    _merge_annotations(host_mir_annotations=host_mir_annotations,
                       guest_mir_annotations=guest_mir_annotations,
                       strategy=strategy)


def exclude_from_mirdatas(host_mir_metadatas: mirpb.MirMetadatas, host_mir_annotations: mirpb.MirAnnotations,
                          mir_root: str, branch_id: str, task_id: str) -> None:
    if not branch_id:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty branch id')
    if not host_mir_metadatas:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid host_mir_metadatas')

    guest_mir_metadatas: mirpb.MirMetadatas = mir_storage_ops.MirStorageOps.load_single_storage(
        mir_root=mir_root, mir_branch=branch_id, mir_task_id=task_id, ms=mirpb.MirStorage.MIR_METADATAS)
    if not guest_mir_metadatas:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                              error_message=f"guest repo {mir_root}:{branch_id} has no metadata.")

    _, _, id_joint = match_asset_ids(set(host_mir_metadatas.attributes.keys()),
                                     set(guest_mir_metadatas.attributes.keys()))
    for asset_id in id_joint:
        del host_mir_metadatas.attributes[asset_id]

        if asset_id in host_mir_annotations.prediction.image_annotations:
            del host_mir_annotations.prediction.image_annotations[asset_id]

        if asset_id in host_mir_annotations.ground_truth.image_annotations:
            del host_mir_annotations.ground_truth.image_annotations[asset_id]

        if asset_id in host_mir_annotations.image_cks:
            del host_mir_annotations.image_cks[asset_id]


def _merge_metadatas(host_mir_metadatas: mirpb.MirMetadatas, guest_mir_metadatas: mirpb.MirMetadatas,
                     id_guest_only: set, id_joint: set, suggested_tvt_type: 'mirpb.TvtType.V',
                     strategy: MergeStrategy) -> None:
    if not host_mir_metadatas or not guest_mir_metadatas:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                              error_message="input host/guest mir_metadatas is invalid")

    # for all ids only in `guest_mir_metadatas`, add them to `host_mir_metadatas`
    for asset_id in id_guest_only:
        host_mir_metadatas.attributes[asset_id].CopyFrom(guest_mir_metadatas.attributes[asset_id])
        if suggested_tvt_type != mirpb.TvtTypeUnknown:
            host_mir_metadatas.attributes[asset_id].tvt_type = suggested_tvt_type
    # for all ids in both two mir_metadatas
    if strategy == MergeStrategy.GUEST:
        for asset_id in id_joint:
            host_mir_metadatas.attributes[asset_id].CopyFrom(guest_mir_metadatas.attributes[asset_id])
            if suggested_tvt_type != mirpb.TvtTypeUnknown:
                host_mir_metadatas.attributes[asset_id].tvt_type = suggested_tvt_type
    elif strategy == MergeStrategy.HOST:
        pass
    elif strategy == MergeStrategy.STOP:
        if len(id_joint) > 0:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_MERGE_ERROR,
                                  error_message='found conflicts in strategy stop')
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"invalid strategy: {strategy}")


def _merge_annotations(host_mir_annotations: mirpb.MirAnnotations, guest_mir_annotations: mirpb.MirAnnotations,
                       strategy: MergeStrategy) -> None:
    """
    add all annotations in guest_mir_annotations into host_mir_annotations

    Args:
        host_mir_annotations (mirpb.MirAnnotations), in/out: host annotations
        guest_mir_annotations (mirpb.MirAnnotations), in: guest annotations
        strategy (MergeStrategy), in: host, guest, stop

    Raises:
        MirRuntimeError: if host or guest annotations empty, or conflicts occured in strategy stop
    """
    _merge_pair_annotations(host_annotation=host_mir_annotations.prediction,
                            guest_annotation=guest_mir_annotations.prediction,
                            strategy=strategy)
    _merge_pair_annotations(host_annotation=host_mir_annotations.ground_truth,
                            guest_annotation=guest_mir_annotations.ground_truth,
                            strategy=strategy)

    _merge_annotation_asset_ids_dict(host_asset_ids_dict=host_mir_annotations.image_cks,
                                     guest_asset_ids_dict=guest_mir_annotations.image_cks,
                                     strategy=strategy)

    host_mir_annotations.prediction.eval_class_ids.extend(guest_mir_annotations.prediction.eval_class_ids)


def _merge_pair_annotations(host_annotation: mirpb.SingleTaskAnnotations, guest_annotation: mirpb.SingleTaskAnnotations,
                            strategy: MergeStrategy) -> None:
    if (host_annotation.type != mirpb.ObjectType.OT_UNKNOWN and guest_annotation.type != mirpb.ObjectType.OT_UNKNOWN
            and host_annotation.type != guest_annotation.type):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_OBJECT_TYPE,
                              error_message='host and guest object type mismatch')

    host_annotation.type = host_annotation.type or guest_annotation.type

    _merge_annotation_asset_ids_dict(host_asset_ids_dict=host_annotation.image_annotations,
                                     guest_asset_ids_dict=guest_annotation.image_annotations,
                                     strategy=strategy)


def _merge_annotation_asset_ids_dict(host_asset_ids_dict: Any,
                                     guest_asset_ids_dict: Any, strategy: MergeStrategy) -> None:
    _, guest_only_ids, joint_ids = match_asset_ids(set(host_asset_ids_dict.keys()),
                                                   set(guest_asset_ids_dict.keys()))
    if strategy == MergeStrategy.STOP and joint_ids:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_MERGE_ERROR,
                              error_message='found conflict image cks in strategy stop')

    asset_ids = (joint_ids | guest_only_ids) if strategy == MergeStrategy.GUEST else guest_only_ids
    for asset_id in asset_ids:
        host_asset_ids_dict[asset_id].CopyFrom(guest_asset_ids_dict[asset_id])


def match_asset_ids(host_ids: set, guest_ids: set) -> Tuple[set, set, set]:
    """
    match asset ids

    Args:
        host_ids (set): host ids
        guest_ids (set): guest ids

    Returns:
        Tuple[set, set, set]: host_only_ids, guest_only_ids, joint_ids
    """
    insets = host_ids & guest_ids
    return (host_ids - insets, guest_ids - insets, insets)
