from collections import defaultdict
import logging
import os
from typing import Dict, List, Tuple, Union

import xmltodict

from mir.tools import class_ids
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb


def _object_dict_to_annotation(object_dict: dict, class_type_manager: class_ids.ClassIdManager) -> mirpb.Annotation:
    bndbox_dict: dict = object_dict['bndbox']
    if not bndbox_dict:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='found no value for bndbox')

    xmin = int(float(bndbox_dict['xmin']))
    ymin = int(float(bndbox_dict['ymin']))
    xmax = int(float(bndbox_dict['xmax']))
    ymax = int(float(bndbox_dict['ymax']))
    width = xmax - xmin + 1
    height = ymax - ymin + 1

    annotation = mirpb.Annotation()
    annotation.class_id = class_type_manager.id_and_main_name_for_name(object_dict['name'])[0]
    annotation.box.x = xmin
    annotation.box.y = ymin
    annotation.box.w = width
    annotation.box.h = height
    annotation.box.rotate_angle = float(object_dict.get('rotate_angle', '-1.0'))
    annotation.score = float(object_dict.get('confidence', '-1.0'))
    annotation.tags.update(object_dict.get('tags', {}))
    annotation.anno_quality = float(object_dict.get('box_quality', '-1.0'))
    return annotation


def import_annotations(mir_metadatas: mirpb.MirMetadatas, mir_annotation: mirpb.MirAnnotations, in_sha1_file: str,
                       in_sha1_gt_file: str, mir_root: str, annotations_dir_path: str, groundtruth_dir_path: str,
                       task_id: str, phase: str) -> Tuple[int, Dict[str, int]]:
    """
    imports annotations

    Args:
        mir_annotation (mirpb.MirAnnotations): data buf for annotations.mir
        mir_keywords (mirpb.MirKeywords): data buf for keywords.mir
        in_sha1_file (str): path to sha1 file
        in_sha1_gt_file (str): path to gt sha1 file
        mir_root (str): path to mir repo
        annotations_dir_path (str): path to annotations root
        groundtruth_dir_path (str): path to groundtruth root
        task_id (str): task id
        phase (str): process phase

    Returns:
        Tuple[int, Dict[str, int]]: return code and unknown type names
    """
    unknown_types_and_count: Dict[str, int] = defaultdict(int)

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.ClassIdManager(mir_root=mir_root)
    logging.info("loaded type id and names: %d", class_type_manager.size())

    if in_sha1_file:
        logging.info(f"wrting annotation in {annotations_dir_path}")
        _import_annotations_from_dir(
            mir_metadatas=mir_metadatas,
            mir_annotation=mir_annotation,
            in_sha1_file=in_sha1_file,
            annotations_dir_path=annotations_dir_path,
            unknown_types_and_count=unknown_types_and_count,
            class_type_manager=class_type_manager,
            image_annotations=mir_annotation.task_annotations[task_id],
        )
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=0.5)

    if groundtruth_dir_path:
        logging.info(f"wrting ground-truth in {groundtruth_dir_path}")
        _import_annotations_from_dir(
            mir_metadatas=mir_metadatas,
            mir_annotation=mir_annotation,
            in_sha1_file=in_sha1_gt_file,
            annotations_dir_path=groundtruth_dir_path,
            unknown_types_and_count=unknown_types_and_count,
            class_type_manager=class_type_manager,
            image_annotations=mir_annotation.ground_truth,
        )
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=1.0)

    return MirCode.RC_OK, unknown_types_and_count


def _import_annotations_from_dir(mir_metadatas: mirpb.MirMetadatas, mir_annotation: mirpb.MirAnnotations,
                                 in_sha1_file: str, annotations_dir_path: str, unknown_types_and_count: Dict[str, int],
                                 class_type_manager: class_ids.ClassIdManager,
                                 image_annotations: mirpb.SingleTaskAnnotations) -> Tuple[int, Dict[str, int]]:

    assethash_filename_list: List[Tuple[str, str]] = []  # hash id and main file name
    with open(in_sha1_file, "r") as in_file:
        for line in in_file.readlines():
            line_components = line.strip().split('\t')
            if not line_components or len(line_components) < 2:
                logging.warning("incomplete line: %s", line)
                continue
            asset_hash, file_name = line_components[0], line_components[1]
            if asset_hash not in mir_metadatas.attributes:
                continue
            main_file_name = os.path.splitext(os.path.basename(file_name))[0]
            assethash_filename_list.append((asset_hash, main_file_name))

    total_assethash_count = len(assethash_filename_list)
    logging.info(f"wrting {total_assethash_count} annotations")

    missing_annotations_counter = 0
    for asset_hash, main_file_name in assethash_filename_list:
        # for each asset, import it's annotations
        annotation_file = os.path.join(annotations_dir_path, main_file_name + '.xml') if annotations_dir_path else None
        if not annotation_file or not os.path.isfile(annotation_file):
            missing_annotations_counter += 1
        else:
            with open(annotation_file, 'r') as f:
                annos_xml_str = f.read()
            if not annos_xml_str:
                logging.error(f"cannot open annotation_file: {annotation_file}")
                return MirCode.RC_CMD_INVALID_ARGS, unknown_types_and_count

            annos_dict: dict = xmltodict.parse(annos_xml_str)['annotation']

            # cks
            mir_annotation.image_cks[asset_hash].cks.update(annos_dict.get('cks', {}))
            mir_annotation.image_cks[asset_hash].image_quality = float(annos_dict.get('image_quality', '-1.0'))

            # annotations and tags
            objects: Union[List[dict], dict] = annos_dict.get('object', [])
            if isinstance(objects, dict):
                # when there's only ONE object node in xml, it will be parsed to a dict, not a list
                objects = [objects]

            anno_idx = 0
            for object_dict in objects:
                type_name = object_dict['name']
                if class_type_manager.has_name(type_name):
                    annotation = _object_dict_to_annotation(object_dict, class_type_manager)
                    annotation.index = anno_idx
                    image_annotations.image_annotations[asset_hash].annotations.append(annotation)
                    anno_idx += 1
                else:
                    unknown_types_and_count[type_name] += 1

    logging.warning(f"asset count that have no annotations: {missing_annotations_counter}")

    return MirCode.RC_OK, unknown_types_and_count
