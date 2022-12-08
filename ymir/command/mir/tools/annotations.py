from collections import defaultdict
import enum
import json
import logging
import os
from typing import Any, Callable, Dict, List, Union

from google.protobuf.json_format import ParseDict
import xmltodict
import yaml

from mir.tools import class_ids
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.settings import COCO_JSON_NAME
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb


class UnknownTypesStrategy(str, enum.Enum):
    STOP = 'stop'
    IGNORE = 'ignore'
    ADD = 'add'


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
        mirpb.ObjectType.OT_SEG: _import_annotations_coco_json,
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
                                    class_type_manager: class_ids.UserLabels) -> mirpb.ObjectAnnotation:
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

    if 'bbox' in anno_dict:
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
    obj_anno.score = anno_dict.get('score', -1)
    obj_anno.anno_quality = anno_dict.get('anno_quality', -1)

    return obj_anno


def import_annotations(mir_annotation: mirpb.MirAnnotations, label_storage_file: str, prediction_dir_path: str,
                       groundtruth_dir_path: str, map_hashed_filename: Dict[str, str],
                       unknown_types_strategy: UnknownTypesStrategy, anno_type: "mirpb.ObjectType.V",
                       phase: str) -> Dict[str, int]:
    anno_import_result: Dict[str, int] = defaultdict(int)

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.load_or_create_userlabels(label_storage_file=label_storage_file)
    logging.info("loaded type id and names: %d", len(class_type_manager.all_ids()))

    if prediction_dir_path:
        logging.info(f"wrting prediction in {prediction_dir_path}")
        _import_annotations_from_dir(
            map_hashed_filename=map_hashed_filename,
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
            map_hashed_filename=map_hashed_filename,
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


def _import_annotations_from_dir(map_hashed_filename: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                 annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                 unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                 image_annotations: mirpb.SingleTaskAnnotations,
                                 anno_type: "mirpb.ObjectType.V") -> None:
    image_annotations.type = anno_type
    _annotation_parse_func(anno_type)(
        map_hashed_filename=map_hashed_filename,
        mir_annotation=mir_annotation,
        annotations_dir_path=annotations_dir_path,
        class_type_manager=class_type_manager,
        unknown_types_strategy=unknown_types_strategy,
        accu_new_class_names=accu_new_class_names,
        image_annotations=image_annotations,
    )

    logging.warning(f"imported {len(image_annotations.image_annotations)} / {len(map_hashed_filename)} annotations")


def _import_annotations_voc_xml(map_hashed_filename: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                image_annotations: mirpb.SingleTaskAnnotations) -> None:
    add_if_not_found = (unknown_types_strategy == UnknownTypesStrategy.ADD)
    for asset_hash, main_file_name in map_hashed_filename.items():
        # for each asset, import it's annotations
        annotation_file = os.path.join(annotations_dir_path, main_file_name + '.xml')
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


def _import_annotations_coco_json(map_hashed_filename: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                  annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                  unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                  image_annotations: mirpb.SingleTaskAnnotations) -> None:
    add_if_not_found = (unknown_types_strategy == UnknownTypesStrategy.ADD)

    coco_file_path = os.path.join(annotations_dir_path, COCO_JSON_NAME)
    with open(coco_file_path, 'r') as f:
        coco_obj = json.loads(f.read())
        images_list = coco_obj['images']
        categories_list = coco_obj['categories']
        annotations_list = coco_obj['annotations']

    if not images_list or not isinstance(images_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find images list in coco json: {coco_file_path}")
    if not categories_list or not isinstance(categories_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find categories list in coco json: {coco_file_path}")
    if annotations_list and not isinstance(annotations_list, list):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_FILE,
                              error_message=f"Can not find annotations list in coco json: {coco_file_path}")

    # images_list -> image_id_to_hashes (key: coco image id, value: ymir asset hash)
    filename_to_hashes = {v: k for k, v in map_hashed_filename.items()}
    image_id_to_hashes: Dict[int, str] = {}
    for v in images_list:
        filename = os.path.splitext(v['file_name'])[0]
        if filename not in filename_to_hashes:
            continue
        image_id_to_hashes[v['id']] = filename_to_hashes[filename]

    # categories_list -> category_id_to_cids (key: coco category id, value: ymir class id)
    category_id_to_cids: Dict[int, int] = {}
    for v in categories_list:
        name = v['name']
        cid, _ = class_type_manager.id_and_main_name_for_name(name)
        if cid < 0:
            accu_new_class_names[name] = 0
            if add_if_not_found:
                cid, _ = class_type_manager.add_main_name(name)
        if cid >= 0:
            category_id_to_cids[v['id']] = cid

    for anno_dict in annotations_list:
        if anno_dict['category_id'] not in category_id_to_cids or anno_dict['image_id'] not in image_id_to_hashes:
            continue

        obj_anno = _coco_object_dict_to_annotation(anno_dict=anno_dict,
                                                   category_id_to_cids=category_id_to_cids,
                                                   class_type_manager=class_type_manager)
        asset_hash = image_id_to_hashes[anno_dict['image_id']]
        obj_anno.index = len(image_annotations.image_annotations[asset_hash].boxes)
        image_annotations.image_annotations[asset_hash].boxes.append(obj_anno)


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
