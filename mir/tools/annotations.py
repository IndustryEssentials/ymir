import logging
import os
from typing import Dict, List, Set, Tuple

import xml.dom.minidom

from mir.tools.code import MirCode
from mir.tools.phase_logger import PhaseLogger, PhaseLoggerCenter, PhaseStateEnum
from mir.protos import mir_command_pb2 as mirpb
from ymir.ids import class_ids


def _get_dom_xml_tag_node(node: xml.dom.minidom.Element, tag_name: str) -> xml.dom.minidom.Element:
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
    raise KeyError(f"found no element for key: {tag_name}")


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
    name = _get_dom_xml_tag_data(obj, "name").lower()
    bndbox_node = _get_dom_xml_tag_node(obj, "bndbox")
    xmin = int(float(_get_dom_xml_tag_data(bndbox_node, "xmin")))
    ymin = int(float(_get_dom_xml_tag_data(bndbox_node, "ymin")))
    xmax = int(float(_get_dom_xml_tag_data(bndbox_node, "xmax")))
    ymax = int(float(_get_dom_xml_tag_data(bndbox_node, "ymax")))
    width = xmax - xmin + 1
    height = ymax - ymin + 1

    annotation = mirpb.Annotation()
    annotation.class_id = class_type_manager.id_and_main_name_for_name(name)[0]
    annotation.box.x = xmin
    annotation.box.y = ymin
    annotation.box.w = width
    annotation.box.h = height
    annotation.score = 0
    return annotation


def _read_customized_Keywords(ck_file: str) -> Dict[str, Set[str]]:
    """
    read customized keywords out from ck file

    Args:
        ck_file (str): tsv file, <asset_name>\t<ck1>\t<ck2>...

    Returns:
        Dict[str, Set[str]]: key: asset name, value: set of customized keywords

    Raises:
        ValueError: if found dumplicat key in ck file
    """
    name_cks = {}  # type: Dict[str, Set[str]]
    if not ck_file:
        return name_cks

    with open(ck_file, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        if not line:
            continue
        components = line.split('\t')
        if len(components) == 1:
            continue

        if components[0] in name_cks:
            raise ValueError(f'dumplicate asset name in ck file: {components[0]}')

        name_cks[components[0]] = set(components[1:])

    return name_cks


def import_annotations(mir_annotation: mirpb.MirAnnotations, mir_keywords: mirpb.MirKeywords, in_sha1_file: str,
                       ck_file: str, annotations_dir_path: str, task_id: str, phase: str) -> int:
    if (not in_sha1_file) or (not annotations_dir_path):
        logging.error("empty sha1_file or annotations_dir_path")
        return MirCode.RC_CMD_INVALID_ARGS

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.ClassIdManager()
    logging.info("loaded type id and names: %d", class_type_manager.size())

    # read customized keywords from ck_file
    cks = _read_customized_Keywords(ck_file)

    image_annotations = mir_annotation.task_annotations[task_id].image_annotations

    assethash_filename_list = []  # type: List[Tuple[str, str, str]]
    with open(in_sha1_file, "r") as in_file:
        for line in in_file.readlines():
            line_components = line.strip().split()
            if not line_components or len(line_components) < 2:
                logging.warning("incomplete line: %s", line)
                continue
            asset_hash, file_name = line_components[0], line_components[1]
            main_file_name = os.path.splitext(os.path.basename(file_name))[0]
            assethash_filename_list.append((asset_hash, main_file_name, file_name))

    total_assethash_count = len(assethash_filename_list)
    logging.info(f"wrting {total_assethash_count} annotations")

    counter = 0
    cur_max_id = class_type_manager._max_id
    missing_annotations_counter = 0
    for asset_hash, main_file_name, file_path in assethash_filename_list:
        annotation_file = os.path.join(annotations_dir_path, main_file_name + '.xml')
        if not os.path.isfile(annotation_file):
            missing_annotations_counter += 1
        else:
            # if have annotation file, import annotations and predefined key ids
            dom_tree = xml.dom.minidom.parse(annotation_file)
            if not dom_tree:
                logging.error("cannot open annotation_file: {}".format(annotation_file))
                return MirCode.RC_CMD_INVALID_ARGS

            single_asset_keyids_set = set()
            collection = dom_tree.documentElement
            objects = collection.getElementsByTagName("object")
            for idx, obj in enumerate(objects):
                annotation = _xml_obj_to_annotation(obj, class_type_manager)
                annotation.index = idx
                image_annotations[asset_hash].annotations.append(annotation)
                single_asset_keyids_set.add(annotation.class_id)
            mir_keywords.keywords[asset_hash].predifined_keyids[:] = single_asset_keyids_set

        # import customized keywords
        if file_path in cks:
            mir_keywords.keywords[asset_hash].customized_keywords[:] = cks[file_path]

        counter += 1
        if counter % 5000 == 0:
            PhaseLoggerCenter.update_phase(phase=phase, local_percent=(counter / total_assethash_count))

    # find extra class ids, save to new file and exit.
    max_id = class_type_manager._max_id
    if max_id > cur_max_id:
        new_ids = [class_type_manager._dirty_id_names_dict[i] for i in range(cur_max_id + 1, max_id + 1)]
        logging.error("\nError: import process abort because new class labels are detected: {}".format(
            ','.join(new_ids)))
        logging.error("new dict file is stored with a .new suffix at: {}".format(class_type_manager._csv_path))
        logging.error("contact ymir-team@intellif.com how to update ids file before continue,")
        logging.error("or use the .new file to replace the previous one a for temp running.")
        return MirCode.RC_CMD_INVALID_ARGS

    if missing_annotations_counter > 0:
        logging.warning(f"asset count that have no annotations: {missing_annotations_counter}")

    return MirCode.RC_OK
