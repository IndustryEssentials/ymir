"""
exports the assets and annotations from mir format to ark-training-format
"""

from collections.abc import Collection
from enum import Enum
import logging
import json
import os
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import xml.etree.ElementTree as ElementTree

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, mir_storage_ops
from mir.tools import utils as mir_utils
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


class ExportError(Exception):
    """
    exception type raised by function `export`
    """
    pass


class ExportFormat(str, Enum):
    EXPORT_FORMAT_UNKNOWN = 'unknown'
    EXPORT_FORMAT_NO_ANNOTATION = 'none'
    EXPORT_FORMAT_ARK = 'ark'
    EXPORT_FORMAT_VOC = 'voc'
    EXPORT_FORMAT_LS_JSON = 'ls_json'  # label studio json format


def check_support_format(anno_format: str) -> bool:
    return anno_format in support_format_type()


def support_format_type() -> List[str]:
    return [f.value for f in ExportFormat]


def format_type_from_str(anno_format: str) -> ExportFormat:
    return ExportFormat(anno_format.lower())


def format_file_ext(anno_format: ExportFormat) -> str:
    _format_ext_map = {
        ExportFormat.EXPORT_FORMAT_ARK: '.txt',
        ExportFormat.EXPORT_FORMAT_VOC: '.xml',
        ExportFormat.EXPORT_FORMAT_LS_JSON: '.json',
    }
    return _format_ext_map[anno_format]


def format_file_output_func(anno_format: ExportFormat) -> Callable:
    _format_func_map = {
        ExportFormat.EXPORT_FORMAT_ARK: _single_image_annotations_to_ark,
        ExportFormat.EXPORT_FORMAT_VOC: _single_image_annotations_to_voc,
        ExportFormat.EXPORT_FORMAT_LS_JSON: _single_image_annotations_to_ls_json,
    }
    return _format_func_map[anno_format]


# public: export
def export(mir_root: str,
           assets_location: str,
           class_type_ids: Dict[int, int],
           asset_ids: Set[str],
           asset_dir: str,
           annotation_dir: str,
           need_ext: bool,
           need_id_sub_folder: bool,
           base_branch: str,
           base_task_id: str,
           format_type: ExportFormat,
           index_file_path: str = None,
           index_prefix: str = None) -> bool:
    """
    export assets and annotations

    Args:
        mir_root (str): path to mir repo root directory
        assets_location (str): path to assets storage directory
        class_type_ids (Dict[int, int]): class ids (and it's mapping value)
            all objects within this dict keys will be exported, if None, export everything;
        asset_ids (Set[str]): export asset ids
        asset_dir (str): asset directory
        annotation_dir (str): annotation directory, if format_type is NO_ANNOTATION, this could be None
        need_ext (bool): if true, all export assets will have it's type as ext, jpg, png, etc.
        need_id_sub_folder (bool): if True, use last 2 chars of asset id as a sub folder name
        base_branch (str): data branch
        format_type (ExportFormat): format type, NONE means exports no annotations
        index_file_path (str | None): path to index file, if None, generates no index file
        index_prefix (str | None): prefix added to each line in index path

    Raises:
        MirRuntimeError

    Returns:
        bool: returns True if success
    """
    if not mir_root:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message="invalid mir_repo",
                              needs_new_commit=False)

    if not check_support_format(format_type):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"invalid --format: {format_type}",
                              needs_new_commit=False)

    # export assets
    os.makedirs(asset_dir, exist_ok=True)
    asset_result = mir_utils.store_assets_to_dir(asset_ids=list(asset_ids),
                                                 out_root=asset_dir,
                                                 sub_folder=".",
                                                 asset_location=assets_location,
                                                 overwrite=False,
                                                 create_prefix=need_id_sub_folder,
                                                 need_suffix=need_ext)

    if index_file_path:
        _generate_asset_index_file(asset_rel_paths=asset_result.values(),
                                   prefix_path=index_prefix,
                                   index_file_path=index_file_path,
                                   overwrite=True)

    if format_type == ExportFormat.EXPORT_FORMAT_NO_ANNOTATION:
        return True

    # export annotations
    mir_datas = mir_storage_ops.MirStorageOps.load(
        mir_root=mir_root,
        mir_branch=base_branch,
        mir_task_id=base_task_id,
        mir_storages=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])
    mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]

    # add all annotations to assets_to_det_annotations_dict
    # key: asset_id as str, value: annotations as List[mirpb.Annotation]
    assets_to_det_annotations_dict = _annotations_by_assets(
        mir_annotations=mir_annotations,
        class_type_ids=set(class_type_ids.keys()) if class_type_ids else None,
        base_task_id=mir_annotations.head_task_id)

    mir_metadatas: mirpb.MirMetadatas = mir_datas[mirpb.MirStorage.MIR_METADATAS]
    _export_detect_annotations_to_path(asset_ids=list(asset_ids),
                                       format_type=format_type,
                                       mir_metadatas=mir_metadatas,
                                       annotations_dict=assets_to_det_annotations_dict,
                                       class_type_mapping=class_type_ids,
                                       dest_path=annotation_dir,
                                       mir_root=mir_root,
                                       assert_id_filename_map=asset_result)

    return True


def _generate_asset_index_file(asset_rel_paths: Collection,
                               prefix_path: Optional[str],
                               index_file_path: str,
                               overwrite: bool = True,
                               image_exts: tuple = ('.jpg', '.jpeg', '.png')) -> None:
    """
    generate index file for export result. in index file, each line is a asset path (in or outside the container)

    Args:
        asset_rel_paths (Collection): the relative asset paths, element type: str
        prefix_path (Optional[str]): prefix path added in front of each element in asset_rel_paths
        index_file_path (str): index file save path
        override (bool): if True, override if file already exists, if False, raise Exception when already exists

    Raise:
        FileExistsError: if index file already exists, and override set to False
    """
    if not asset_rel_paths or not index_file_path:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty asset_rel_paths or index_file_path')
    if os.path.exists(index_file_path):
        if overwrite:
            logging.warning(f"index file already exists, overwriting: {index_file_path}")
        else:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"index file already exists: {index_file_path}")

    with open(index_file_path, 'w') as f:
        for item in asset_rel_paths:
            if os.path.splitext(item)[1] not in image_exts:
                logging.warning(f"unsupported image ext in path: {item}")
                continue
            f.write((os.path.join(prefix_path, item) if prefix_path else item) + '\n')


# private: export annotations: general
def _annotations_by_assets(mir_annotations: mirpb.MirAnnotations, class_type_ids: Optional[Set[int]],
                           base_task_id: str) -> Dict[str, List[mirpb.Annotation]]:
    """
    get annotations by assets

    Args:
        mir_annotations (mirpb.MirAnnotations): annotations
        class_type_ids (Optional[Set[int]]): only type ids within it could be output, if None, no id filter applied
        base_task_id (str): base task id

    Returns:
        Dict, key: asset id, value: List[mirpb.Annotation]
    """
    assets_to_det_annotations_dict = {}  # type: Dict[str, List[mirpb.Annotation]]

    if base_task_id not in mir_annotations.task_annotations:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                              error_message=f"base task id: {base_task_id} not in mir_annotations")

    task_annotations = mir_annotations.task_annotations[base_task_id]
    for asset_id, image_annotations in task_annotations.image_annotations.items():
        matched_annotations = [
            annotation for annotation in image_annotations.annotations
            if (not class_type_ids or (annotation.class_id in class_type_ids))
        ]
        assets_to_det_annotations_dict[asset_id] = matched_annotations

    return assets_to_det_annotations_dict


def _export_detect_annotations_to_path(asset_ids: List[str], format_type: ExportFormat,
                                       mir_metadatas: mirpb.MirMetadatas,
                                       annotations_dict: Dict[str, List[mirpb.Annotation]],
                                       class_type_mapping: Optional[Dict[int, int]], dest_path: str, mir_root: str,
                                       assert_id_filename_map: Dict[str, str]) -> None:
    if not asset_ids:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty asset_ids')
    if not mir_metadatas:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid mir_metadatas')

    os.makedirs(dest_path, exist_ok=True)

    cls_id_mgr = class_ids.ClassIdManager(mir_root=mir_root)

    missing_counter = 0
    empty_counter = 0
    for asset_id in asset_ids:
        if asset_id not in mir_metadatas.attributes:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_FILE,
                                  error_message=f"can not find asset id: {asset_id} in mir_metadatas")
        attrs = mir_metadatas.attributes[asset_id]

        if asset_id not in annotations_dict:
            missing_counter += 1
            annotations = []
        else:
            annotations = annotations_dict[asset_id]
        if len(annotations) == 0:
            empty_counter += 1

        format_func = format_file_output_func(anno_format=format_type)
        anno_str = format_func(asset_id=asset_id,
                               attrs=attrs,
                               annotations=annotations,
                               class_type_mapping=class_type_mapping,
                               cls_id_mgr=cls_id_mgr,
                               asset_filename=assert_id_filename_map[asset_id])
        with open(os.path.join(dest_path, f"{asset_id}{format_file_ext(format_type)}"), 'w') as f:
            f.write(anno_str)

    logging.info(f"missing annotations: {missing_counter}, "
                 f"empty annotations: {empty_counter} out of {len(asset_ids)} assets")


def _single_image_annotations_to_ark(asset_id: str, attrs: Any, annotations: List[mirpb.Annotation],
                                     class_type_mapping: Optional[Dict[int, int]], cls_id_mgr: class_ids.ClassIdManager,
                                     asset_filename: str) -> str:
    output_str = ""
    for annotation in annotations:
        mapped_id = class_type_mapping[annotation.class_id] if class_type_mapping else annotation.class_id
        output_str += f"{mapped_id}, {annotation.box.x}, {annotation.box.y}, "
        output_str += f"{annotation.box.x + annotation.box.w - 1}, {annotation.box.y + annotation.box.h - 1}\n"
    return output_str


def _single_image_annotations_to_voc(asset_id: str, attrs: Any, annotations: List[mirpb.Annotation],
                                     class_type_mapping: Optional[Dict[int, int]], cls_id_mgr: class_ids.ClassIdManager,
                                     asset_filename: str) -> str:
    # annotation
    annotation_node = ElementTree.Element('annotation')

    # annotation: folder
    folder_node = ElementTree.SubElement(annotation_node, 'folder')
    folder_node.text = 'folder'

    # annotation: filename
    filename_node = ElementTree.SubElement(annotation_node, 'filename')
    filename_node.text = asset_filename

    # annotation: source
    source_node = ElementTree.SubElement(annotation_node, 'source')

    # annotation: source: database
    database_node = ElementTree.SubElement(source_node, 'database')
    database_node.text = attrs.dataset_name or 'unknown'

    # annotation: source: annotation
    annotation2_node = ElementTree.SubElement(source_node, 'annotation')
    annotation2_node.text = 'unknown'

    # annotation: source: image
    image_node = ElementTree.SubElement(source_node, 'image')
    image_node.text = 'unknown'

    # annotation: size
    size_node = ElementTree.SubElement(annotation_node, 'size')

    # annotation: size: width
    width_node = ElementTree.SubElement(size_node, 'width')
    width_node.text = str(attrs.width)

    # annotation: size: height
    height_node = ElementTree.SubElement(size_node, 'height')
    height_node.text = str(attrs.height)

    # annotation: size: depth
    depth_node = ElementTree.SubElement(size_node, 'depth')
    depth_node.text = str(attrs.image_channels)

    # annotation: segmented
    segmented_node = ElementTree.SubElement(annotation_node, 'segmented')
    segmented_node.text = '0'

    # annotation: object(s)
    for annotation in annotations:
        object_node = ElementTree.SubElement(annotation_node, 'object')

        name_node = ElementTree.SubElement(object_node, 'name')
        name_node.text = cls_id_mgr.main_name_for_id(annotation.class_id) or 'unknown'

        pose_node = ElementTree.SubElement(object_node, 'pose')
        pose_node.text = 'unknown'

        truncated_node = ElementTree.SubElement(object_node, 'truncated')
        truncated_node.text = 'unknown'

        occluded_node = ElementTree.SubElement(object_node, 'occluded')
        occluded_node.text = '0'

        bndbox_node = ElementTree.SubElement(object_node, 'bndbox')

        xmin_node = ElementTree.SubElement(bndbox_node, 'xmin')
        xmin_node.text = str(annotation.box.x)

        ymin_node = ElementTree.SubElement(bndbox_node, 'ymin')
        ymin_node.text = str(annotation.box.y)

        xmax_node = ElementTree.SubElement(bndbox_node, 'xmax')
        xmax_node.text = str(annotation.box.x + annotation.box.w - 1)

        ymax_node = ElementTree.SubElement(bndbox_node, 'ymax')
        ymax_node.text = str(annotation.box.y + annotation.box.h - 1)

        difficult_node = ElementTree.SubElement(object_node, 'difficult')
        difficult_node.text = '0'

    return ElementTree.tostring(element=annotation_node, encoding='unicode')


def _single_image_annotations_to_ls_json(asset_id: str, attrs: Any, annotations: List[mirpb.Annotation],
                                         class_type_mapping: Optional[Dict[int, int]],
                                         cls_id_mgr: class_ids.ClassIdManager, asset_filename: str) -> str:
    out_type = "predictions"  # out_type: annotation type - "annotations" or "predictions"
    to_name = 'image'  # to_name: object name from Label Studio labeling config
    from_name = 'label'  # control tag name from Label Studio labeling config
    task: Dict = {
        out_type: [{
            "result": [],
            "ground_truth": False,
        }],
        "data": {
            "image": asset_filename
        }
    }

    for annotation in annotations:
        bbox_x, bbox_y = float(annotation.box.x), float(annotation.box.y)
        bbox_width, bbox_height = float(annotation.box.w), float(annotation.box.h)
        img_width, img_height = attrs.width, attrs.height
        item = {
            "id": uuid.uuid4().hex[0:10],  # random id to identify this annotation.
            "type": "rectanglelabels",
            "value": {
                # Units of image annotations in label studio is percentage of image width/height.
                # https://labelstud.io/guide/predictions.html#Units-of-image-annotations
                "x": bbox_x / img_width * 100,
                "y": bbox_y / img_height * 100,
                "width": bbox_width / img_width * 100,
                "height": bbox_height / img_height * 100,
                "rotation": 0,
                "rectanglelabels": [cls_id_mgr.main_name_for_id(annotation.class_id) or 'unknown']
            },
            "to_name": to_name,
            "from_name": from_name,
            "image_rotation": 0,
            "original_width": img_width,
            "original_height": img_height
        }
        task[out_type][0]['result'].append(item)
    return json.dumps(task)
