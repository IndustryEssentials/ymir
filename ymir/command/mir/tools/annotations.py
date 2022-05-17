from collections import defaultdict
import logging
import os
from typing import Dict, List, Optional, Tuple

import xml.dom.minidom

from mir.tools import class_ids
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
from mir.tools.phase_logger import PhaseLoggerCenter
from mir.protos import mir_command_pb2 as mirpb


def _get_dom_xml_tag_node(node: xml.dom.minidom.Element, tag_name: str) -> Optional[xml.dom.minidom.Element]:
    """
    suppose we have the following xml:
    ```
    <blabla>
        <tag1>tag1_value</tag1>
        <tag2>tag2_value</tag2>
    </blabla>
    ```
    and we have node point to <blabla>, we can use this function to get node tag1 and tag2 \n
    if tag not found, returns None
    """
    tag_nodes = node.getElementsByTagName(tag_name)
    if len(tag_nodes) > 0 and len(tag_nodes[0].childNodes) > 0:
        return tag_nodes[0]
    return None


def _get_dom_xml_tag_data(node: xml.dom.minidom.Element, tag_name: str) -> str:
    """
    suppose we have the following xml:
    ```
    <blabla>
        <tag1>tag1_value</tag1>
        <tag2>tag2_value</tag2>
    </blabla>
    ```
    and we have node point to <blabla>, we can use this function to get tag1_value and tag2_value \n
    if tag not found, returns empty str
    """
    tag_node = _get_dom_xml_tag_node(node, tag_name)
    if tag_node and len(tag_node.childNodes) > 0:
        return tag_node.childNodes[0].data
    return ''


def _xml_obj_to_annotation(obj: xml.dom.minidom.Element,
                           class_type_manager: class_ids.ClassIdManager) -> mirpb.Annotation:
    """
    generate mirpb.Annotation instance from object node in coco and pascal annotation xml file
    """
    name = _xml_obj_to_type_name(obj)
    bndbox_node = _get_dom_xml_tag_node(obj, "bndbox")
    if not bndbox_node:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='found no value for bndbox')

    xmin = int(float(_get_dom_xml_tag_data(bndbox_node, "xmin")))
    ymin = int(float(_get_dom_xml_tag_data(bndbox_node, "ymin")))
    xmax = int(float(_get_dom_xml_tag_data(bndbox_node, "xmax")))
    ymax = int(float(_get_dom_xml_tag_data(bndbox_node, "ymax")))
    width = xmax - xmin + 1
    height = ymax - ymin + 1

    # there's no `score` key in original voc format, we add it here to support box conf score
    score_str = _get_dom_xml_tag_data(obj, 'score')
    score = float(score_str) if score_str else 2.0

    annotation = mirpb.Annotation()
    annotation.class_id = class_type_manager.id_and_main_name_for_name(name)[0]
    annotation.box.x = xmin
    annotation.box.y = ymin
    annotation.box.w = width
    annotation.box.h = height
    annotation.score = score
    return annotation


def _xml_obj_to_type_name(obj: xml.dom.minidom.Element) -> str:
    return _get_dom_xml_tag_data(obj, "name").lower()


def import_annotations(mir_metadatas: mirpb.MirMetadatas, mir_annotation: mirpb.MirAnnotations,
                       in_sha1_file: str, mir_root: str,
                       annotations_dir_path: str, task_id: str, phase: str) -> Tuple[int, Dict[str, int]]:
    """
    imports annotations

    Args:
        mir_annotation (mirpb.MirAnnotations): data buf for annotations.mir
        mir_keywords (mirpb.MirKeywords): data buf for keywords.mir
        in_sha1_file (str): path to sha1 file
        mir_root (str): path to mir repo
        annotations_dir_path (str): path to annotations root
        task_id (str): task id
        phase (str): process phase

    Returns:
        Tuple[int, Dict[str, int]]: return code and unknown type names
    """
    unknown_types_and_count: Dict[str, int] = defaultdict(int)

    if not in_sha1_file:
        logging.error("empty sha1_file")
        return MirCode.RC_CMD_INVALID_ARGS, unknown_types_and_count

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.ClassIdManager(mir_root=mir_root)
    logging.info("loaded type id and names: %d", class_type_manager.size())

    image_annotations = mir_annotation.task_annotations[task_id].image_annotations

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

    counter = 0
    missing_annotations_counter = 0
    for asset_hash, main_file_name in assethash_filename_list:
        # for each asset, import it's annotations
        annotation_file = os.path.join(annotations_dir_path, main_file_name + '.xml') if annotations_dir_path else None
        if not annotation_file or not os.path.isfile(annotation_file):
            missing_annotations_counter += 1
        else:
            # if have annotation file, import annotations and predefined key ids
            dom_tree = xml.dom.minidom.parse(annotation_file)
            if not dom_tree:
                logging.error(f"cannot open annotation_file: {annotation_file}")
                return MirCode.RC_CMD_INVALID_ARGS, unknown_types_and_count

            collection = dom_tree.documentElement
            objects = collection.getElementsByTagName("object")
            for idx, obj in enumerate(objects):
                type_name = _xml_obj_to_type_name(obj)
                if class_type_manager.has_name(type_name):
                    annotation = _xml_obj_to_annotation(obj, class_type_manager)
                    annotation.index = idx
                    image_annotations[asset_hash].annotations.append(annotation)
                else:
                    unknown_types_and_count[type_name] += 1

        counter += 1
        if counter % 5000 == 0:
            PhaseLoggerCenter.update_phase(phase=phase, local_percent=(counter / total_assethash_count))

    if missing_annotations_counter > 0:
        logging.warning(f"asset count that have no annotations: {missing_annotations_counter}")

    return MirCode.RC_OK, unknown_types_and_count
