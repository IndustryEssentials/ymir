from collections import defaultdict
import enum
import io
import json
import logging
import os
from PIL import Image, UnidentifiedImageError
from typing import Any, Callable, Dict, List, Set, Tuple, Union

from google.protobuf.json_format import ParseDict
import xmltodict
import yaml

from mir.tools import class_ids
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb


class UnknownTypesStrategy(str, enum.Enum):
    STOP = 'stop'
    IGNORE = 'ignore'
    ADD = 'add'


def parse_anno_format(anno_format_str: str) -> "mirpb.AnnoFormat.V":
    _anno_dict: Dict[str, mirpb.AnnoFormat.V] = {
        # compatible with legacy format.
        "voc": mirpb.AnnoFormat.AF_DET_PASCAL_VOC,
        "ark": mirpb.AnnoFormat.AF_DET_ARK_JSON,
        "ls_json": mirpb.AnnoFormat.AF_DET_LS_JSON,
        "det-voc": mirpb.AnnoFormat.AF_DET_PASCAL_VOC,
        "det-ark": mirpb.AnnoFormat.AF_DET_ARK_JSON,
        "det-ls-json": mirpb.AnnoFormat.AF_DET_LS_JSON,
        "seg-poly": mirpb.AnnoFormat.AF_SEG_POLYGON,
        "seg-mask": mirpb.AnnoFormat.AF_SEG_MASK,
    }
    return _anno_dict.get(anno_format_str.lower(), mirpb.AnnoFormat.AF_NO_ANNOTATION)


def parse_anno_type(anno_type_str: str) -> "mirpb.AnnoType.V":
    _anno_dict: Dict[str, mirpb.AnnoType.V] = {
        "det-box": mirpb.AnnoType.AT_DET_BOX,
        "seg-poly": mirpb.AnnoType.AT_SEG_POLYGON,
        "seg-mask": mirpb.AnnoType.AT_SEG_MASK,
    }
    return _anno_dict.get(anno_type_str.lower(), mirpb.AnnoType.AT_UNKNOWN)


def _annotation_parse_func(anno_type: "mirpb.AnnoType.V") -> Callable:
    _func_dict: Dict["mirpb.AnnoType.V", Callable] = {
        mirpb.AnnoType.AT_DET_BOX: _import_annotations_voc_xml,
        mirpb.AnnoType.AT_SEG_POLYGON: _import_annotations_voc_xml,
        mirpb.AnnoType.AT_SEG_MASK: _import_annotations_seg_mask,
    }
    if anno_type not in _func_dict:
        raise NotImplementedError
    return _func_dict[anno_type]


def _object_dict_to_annotation(object_dict: dict, cid: int) -> mirpb.ObjectAnnotation:
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
    elif object_dict.get('polygon'):
        raise NotImplementedError
    else:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='no value for bndbox or polygon')
    return annotation


def import_annotations(mir_annotation: mirpb.MirAnnotations, mir_root: str, prediction_dir_path: str,
                       groundtruth_dir_path: str, map_hashed_filename: Dict[str, str],
                       unknown_types_strategy: UnknownTypesStrategy, anno_type: "mirpb.AnnoType.V",
                       phase: str) -> Dict[str, int]:
    anno_import_result: Dict[str, int] = defaultdict(int)

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.load_or_create_userlabels(mir_root=mir_root)
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
                                 image_annotations: mirpb.SingleTaskAnnotations, anno_type: "mirpb.AnnoType.V") -> None:
    # temp solution: set to seg type if SegmentationClass and labelmap.txt exist.
    # will be removed once seg type can be passed via web.
    if (os.path.isdir(os.path.join(annotations_dir_path, "SegmentationClass"))
            and os.path.isfile(os.path.join(annotations_dir_path, "labelmap.txt"))):
        anno_type = mirpb.AnnoType.AT_SEG_MASK

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


def _import_annotations_seg_mask(map_hashed_filename: Dict[str, str], mir_annotation: mirpb.MirAnnotations,
                                 annotations_dir_path: str, class_type_manager: class_ids.UserLabels,
                                 unknown_types_strategy: UnknownTypesStrategy, accu_new_class_names: Dict[str, int],
                                 image_annotations: mirpb.SingleTaskAnnotations) -> None:
    # fortmat ref:
    # https://github.com/acesso-io/techcore-cvat/tree/develop/cvat/apps/dataset_manager/formats#segmentation-mask-import
    # single line reprs label&color map, e.g. "ego vehicle:0,181,0::" or "road:07::"; otherwise "..." for place-holder.
    label_map_file = os.path.join(annotations_dir_path, 'labelmap.txt')
    if not os.path.isfile(label_map_file):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="labelmap.txt is required.")
    with open(label_map_file) as f:
        records = f.readlines()

    # parse label_map.txt into map_cname_color.
    map_cname_color: Dict[str, Tuple[int, int, int]] = {}
    for record in records:
        record = record.strip()
        if ':' not in record or not record:
            logging.info("place-holder line, skipping.")
            continue

        record_split = record.split(':')
        if len(record_split) != 4:
            logging.info(f"invalid labelmap line: {record}")
            continue
        pos_ints: List[int] = [int(x) for x in record_split[1].split(',')]
        if len(pos_ints) == 1:  # single channel to 3 channels.
            pos_ints = [pos_ints[0], pos_ints[0], pos_ints[0]]
        if len(pos_ints) != 3:
            logging.info(f"invalid labelmap color idx: {pos_ints}")
            continue
        if pos_ints == (0, 0, 0):
            logging.info("ignore background color.")
            continue
        _, cname = class_type_manager.id_and_main_name_for_name(name=record_split[0])
        map_cname_color[cname] = (pos_ints[0], pos_ints[1], pos_ints[2])

    # batch add all names, including unknown/known names.
    if unknown_types_strategy == UnknownTypesStrategy.ADD:
        class_type_manager.add_main_names(list(map_cname_color.keys()))

    # build color map, map all unknown classes to background (0, 0, 0).
    map_color_pixel: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {(0, 0, 0): (0, 0, 0)}
    map_color_cid: Dict[Tuple[int, int, int], int] = {}
    for name, color in map_cname_color.items():
        cid, cname = class_type_manager.id_and_main_name_for_name(name=name)
        if cname not in accu_new_class_names:
            accu_new_class_names[cname] = 0

        if cid >= 0:
            point = mirpb.IntPoint()
            point.x, point.y, point.z = color
            image_annotations.map_id_color[cid].CopyFrom(point)
            map_color_pixel[color] = color
            map_color_cid[color] = cid
        else:
            map_color_pixel[color] = (0, 0, 0)

    semantic_mask_dir = os.path.join(annotations_dir_path, "SegmentationClass")
    unexpected_color: Set[Tuple[int, int, int]] = set()
    for asset_hash, main_file_name in map_hashed_filename.items():
        # for each asset, import it's annotations
        annotation_file = os.path.join(semantic_mask_dir, main_file_name + '.png')
        if not os.path.isfile(annotation_file):
            continue
        try:
            mask_image = Image.open(annotation_file)
        except (UnidentifiedImageError, OSError) as e:
            logging.info(f"{type(e).__name__}: {e}\nannotation_file: {annotation_file}\n")
            continue
        asset_type_str: str = mask_image.format.lower()
        if asset_type_str != 'png':
            logging.error(f"cannot import annotation_file: {annotation_file} as type: {asset_type_str}")
            continue

        mask_image = mask_image.convert('RGB')
        img_class_ids: Set[int] = set()
        width, height = mask_image.size
        for x in range(width):
            for y in range(height):
                color = mask_image.getpixel((x, y))
                if color in map_color_pixel:
                    unexpected_color.add(color)

                # map_color_cid (known class names) is subset of map_color_pixel (including known/unknown).
                if color in map_color_cid:
                    img_class_ids.add(map_color_cid[color])
                elif color != (0, 0, 0):  # map unknown color to (0,0,0).
                    mask_image.putpixel((x, y), (0, 0, 0))
        with io.BytesIO() as output:
            mask_image.save(output, format="PNG")
            image_annotations.image_annotations[asset_hash].mask.semantic_mask = output.getvalue()
        image_annotations.image_annotations[asset_hash].img_class_ids[:] = list(img_class_ids)
    if unexpected_color:
        logging.info(f"find color not in labelmap.txt: {unexpected_color}")


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
                annotation = _object_dict_to_annotation(object_dict, cid)
                annotation.index = anno_idx
                image_annotations.image_annotations[asset_hash].boxes.append(annotation)
                anno_idx += 1


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
