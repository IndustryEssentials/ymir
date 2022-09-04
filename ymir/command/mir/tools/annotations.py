from collections import defaultdict
import enum
from io import StringIO
import logging
import os
from typing import Dict, List, Tuple, Union

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


class ClassTypeIdAndCount:
    def __init__(self, id: int = -1, count: int = 0) -> None:
        self.id = id
        self.count = count

    def __repr__(self) -> str:
        return '{' + f"id: {self.id}, count: {self.count}" + '}'


AnnoNewTypes = Dict[str, ClassTypeIdAndCount]


def _object_dict_to_annotation(object_dict: dict, cid: int) -> mirpb.Annotation:
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
    annotation.class_id = cid
    annotation.box.x = xmin
    annotation.box.y = ymin
    annotation.box.w = width
    annotation.box.h = height
    annotation.box.rotate_angle = float(bndbox_dict.get('rotate_angle', '0.0'))
    annotation.score = float(object_dict.get('confidence', '-1.0'))
    tags = object_dict.get('tags', {})  # tags could be None
    if tags:
        annotation.tags.update(tags)
    annotation.anno_quality = float(object_dict.get('box_quality', '-1.0'))
    return annotation


def import_annotations(mir_metadatas: mirpb.MirMetadatas, mir_annotation: mirpb.MirAnnotations, in_sha1_file: str,
                       in_sha1_gt_file: str, mir_root: str, prediction_dir_path: str, groundtruth_dir_path: str,
                       unknown_types_strategy: UnknownTypesStrategy, task_id: str, phase: str) -> AnnoNewTypes:
    """
    imports annotations

    Args:
        mir_annotation (mirpb.MirAnnotations): data buf for annotations.mir
        mir_keywords (mirpb.MirKeywords): data buf for keywords.mir
        in_sha1_file (str): path to sha1 file
        in_sha1_gt_file (str): path to gt sha1 file
        mir_root (str): path to mir repo
        prediction_dir_path (str): path to annotations root
        groundtruth_dir_path (str): path to groundtruth root
        unknown_types_strategy (UnknownTypesStrategy): strategy for unknown types
        task_id (str): task id
        phase (str): process phase

    Returns:
        AnnoImportResult: added types and unknown (ignored) types

    Raises:
        MirRuntimeError if strategy is STOP and have unknown types
    """

    anno_import_result: Dict[str, ClassTypeIdAndCount] = defaultdict(ClassTypeIdAndCount)

    # read type_id_name_dict and type_name_id_dict
    class_type_manager = class_ids.ClassIdManager(mir_root=mir_root)
    logging.info("loaded type id and names: %d", len(class_type_manager.all_ids()))

    if prediction_dir_path:
        logging.info(f"wrting prediction in {prediction_dir_path}")
        _import_annotations_from_dir(
            mir_metadatas=mir_metadatas,
            mir_annotation=mir_annotation,
            in_sha1_file=in_sha1_file,
            annotations_dir_path=prediction_dir_path,
            class_type_manager=class_type_manager,
            unknown_types_strategy=unknown_types_strategy,
            accu_new_types=anno_import_result,
            image_annotations=mir_annotation.prediction,
        )
        _import_annotation_meta(mir_root=mir_root,
                                annotations_dir_path=prediction_dir_path,
                                task_annotations=mir_annotation.prediction)
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=0.5)

    if groundtruth_dir_path:
        logging.info(f"wrting ground-truth in {groundtruth_dir_path}")
        _import_annotations_from_dir(
            mir_metadatas=mir_metadatas,
            mir_annotation=mir_annotation,
            in_sha1_file=in_sha1_gt_file,
            annotations_dir_path=groundtruth_dir_path,
            class_type_manager=class_type_manager,
            unknown_types_strategy=unknown_types_strategy,
            accu_new_types=anno_import_result,
            image_annotations=mir_annotation.ground_truth,
        )
    PhaseLoggerCenter.update_phase(phase=phase, local_percent=1.0)

    if unknown_types_strategy == UnknownTypesStrategy.STOP and anno_import_result:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_UNKNOWN_TYPES,
                              error_message=f"{list(anno_import_result.keys())}")

    return anno_import_result


def _import_annotations_from_dir(mir_metadatas: mirpb.MirMetadatas, mir_annotation: mirpb.MirAnnotations,
                                 in_sha1_file: str, annotations_dir_path: str,
                                 class_type_manager: class_ids.ClassIdManager,
                                 unknown_types_strategy: UnknownTypesStrategy, accu_new_types: AnnoNewTypes,
                                 image_annotations: mirpb.SingleTaskAnnotations) -> None:
    """
    import annotations from root dir of voc annotation files

    Args:
        mir_metadatas (mirpb.MirMetadatas): list of asset metadatas
        mir_annotations (mirpb.MirAnnotations): instance of annotations
        in_sha1_file (str): path to sha1 file, in each line: asset path and sha1sum
        annotations_dir_path (str): path to prediction / gt dir
        class_type_manager (class_ids.ClassIdManager): class types manager
        accu_anno_import_result (AnnoImportResult): accumulated annotation import result
        unknown_types_strategy (UnknownTypesStrategy): strategy of unknown type names
        image_annotations (mirpb.SingleTaskAnnotations): asset ids and annotations
    """

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
    add_if_not_found = (unknown_types_strategy == UnknownTypesStrategy.ADD)
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

                # update set of new_types, add label if required.
                if cid < 0:
                    if add_if_not_found:
                        cid, _ = class_type_manager.add_main_name(main_name=new_type_name)
                    accu_new_types[new_type_name].id = cid

                # update counts of new types.
                if new_type_name in accu_new_types:
                    accu_new_types[new_type_name].count += 1

                if cid >= 0:
                    annotation = _object_dict_to_annotation(object_dict, cid)
                    annotation.index = anno_idx
                    image_annotations.image_annotations[asset_hash].annotations.append(annotation)
                    anno_idx += 1

    logging.warning(f"asset count that have no annotations: {missing_annotations_counter}")


def _import_annotation_meta(mir_root: str, annotations_dir_path: str,
                            task_annotations: mirpb.SingleTaskAnnotations) -> None:
    annotation_meta_path = os.path.join(annotations_dir_path, 'meta.yaml')
    if not os.path.isfile(annotation_meta_path):
        return

    with open(annotation_meta_path, 'r') as f:
        annotation_meta_dict = yaml.safe_load(f)

    # model
    if 'model' in annotation_meta_dict:
        ParseDict(annotation_meta_dict['model'], task_annotations.model)

    # eval_class_ids
    eval_class_names = annotation_meta_dict.get('eval_class_names', []) or task_annotations.model.class_names
    task_annotations.eval_class_ids[:] = class_ids.ClassIdManager(mir_root=mir_root).id_for_names(
        list(eval_class_names))[0]

    # executor_config
    if 'executor_config' in annotation_meta_dict:
        executor_config_str_io = StringIO()
        yaml.safe_dump(annotation_meta_dict['executor_config'], executor_config_str_io)
        task_annotations.executor_config = executor_config_str_io.getvalue()
