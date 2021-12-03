"""
exports the assets and annotations from mir format to ark-training-format
"""

from collections.abc import Collection
from enum import Enum
import logging
import os
from typing import Any, Dict, List, Optional, Set
import xml.etree.ElementTree as ElementTree

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, mir_storage_ops
from mir.tools import utils as mir_utils
from mir.tools.phase_logger import PhaseLoggerCenter, PhaseStateEnum


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


# public: format type
SUPPORTED_EXPORT_FORMATS = {
    ExportFormat.EXPORT_FORMAT_NO_ANNOTATION.value, ExportFormat.EXPORT_FORMAT_ARK.value,
    ExportFormat.EXPORT_FORMAT_VOC.value
}


def format_type_from_str(format: str) -> ExportFormat:
    return ExportFormat(format.lower())


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
        ValueError: if mir repo not provided

    Returns:
        bool: returns True if success
    """
    if not mir_root:
        raise ValueError("invalid mir_repo")

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
        mir_storages=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])
    mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]

    # add all annotations to assets_to_det_annotations_dict
    # key: asset_id as str, value: annotations as List[mirpb.Annotation]
    assets_to_det_annotations_dict = _annotations_by_assets(
        mir_annotations=mir_annotations,
        class_type_ids=set(class_type_ids.keys()) if class_type_ids else None,
        base_task_id=mir_annotations.head_task_id)

    if format_type == ExportFormat.EXPORT_FORMAT_ARK:
        _export_detect_ark_annotations_to_path(annotations_dict=assets_to_det_annotations_dict,
                                               asset_ids=list(asset_ids),
                                               dest_path=annotation_dir,
                                               class_type_mapping=class_type_ids)
    elif format_type == ExportFormat.EXPORT_FORMAT_VOC:
        mir_metadatas: mirpb.MirMetadatas = mir_datas[mirpb.MirStorage.MIR_METADATAS]
        _export_detect_voc_annotations_to_path(annotations_dict=assets_to_det_annotations_dict,
                                               mir_metadatas=mir_metadatas,
                                               asset_ids=list(asset_ids),
                                               dest_path=annotation_dir,
                                               mir_root=mir_root)
    else:
        raise ValueError(f"unsupported format: {format_type.name}")

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
        raise ValueError('empty asset_rel_paths or index_file_path')
    if os.path.exists(index_file_path):
        if overwrite:
            logging.warning(f"index file already exists, overwriting: {index_file_path}")
        else:
            raise FileExistsError(f"index file already exists: {index_file_path}")

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
        raise ValueError(f"base task id: {base_task_id} not in mir_annotations")

    task_annotations = mir_annotations.task_annotations[base_task_id]
    for asset_id, image_annotations in task_annotations.image_annotations.items():
        matched_annotations = [
            annotation for annotation in image_annotations.annotations
            if (not class_type_ids or (annotation.class_id in class_type_ids))
        ]
        assets_to_det_annotations_dict[asset_id] = matched_annotations

    return assets_to_det_annotations_dict


# private: export annotations: ark
def _export_detect_ark_annotations_to_path(annotations_dict: Dict[str, List[mirpb.Annotation]], asset_ids: List[str],
                                           dest_path: str, class_type_mapping: Optional[Dict[int, int]]) -> None:
    if not asset_ids:
        raise ValueError("empty asset ids")

    os.makedirs(dest_path, exist_ok=True)

    missing_counter = 0
    empty_counter = 0
    for asset_id in asset_ids:
        # calc missing or empty
        if asset_id not in annotations_dict:
            missing_counter += 1
            continue
        annotations = annotations_dict[asset_id]
        if len(annotations) == 0:
            empty_counter += 1
            continue

        file_name = f"{asset_id}.txt"
        dest_file_path = os.path.join(dest_path, file_name)
        _single_image_annotations_to_ark(annotations, dest_file_path, class_type_mapping)

    if missing_counter > 0 or empty_counter > 0:
        logging.warning(f"missing annotations assets: {missing_counter}, "
                        f"empty annotations assets: {empty_counter} out of {len(asset_ids)}")


# private: export annotations: voc
def _export_detect_voc_annotations_to_path(annotations_dict: Dict[str, List[mirpb.Annotation]],
                                           mir_metadatas: mirpb.MirMetadatas, asset_ids: List[str],
                                           dest_path: str, mir_root: str) -> None:
    if not asset_ids:
        raise ValueError('empty asset_ids')
    if not mir_metadatas:
        raise ValueError('invalid mir_metadatas')

    os.makedirs(dest_path, exist_ok=True)

    cls_id_mgr = class_ids.ClassIdManager(mir_root=mir_root)

    missing_counter = 0
    empty_counter = 0
    for asset_id in asset_ids:
        if asset_id not in mir_metadatas.attributes:
            raise ValueError(f"can not find asset id: {asset_id} in mir_metadatas")

        if asset_id not in annotations_dict:
            missing_counter += 1
            continue
        annotations = annotations_dict[asset_id]
        if len(annotations) == 0:
            empty_counter += 1
            continue

        attrs = mir_metadatas.attributes[asset_id]
        annotations = annotations_dict[asset_id]

        file_name = f"{asset_id}.xml"
        dest_file_path = os.path.join(dest_path, file_name)
        _single_image_annotations_to_voc(asset_id, attrs, annotations, dest_file_path, cls_id_mgr)

    if missing_counter > 0:
        logging.warning(f"missing annotations assets: {missing_counter}, empty annotations assets: {empty_counter}")


def _single_image_annotations_to_ark(annotations: List[mirpb.Annotation], dest_file_path: str,
                                     class_type_mapping: Optional[Dict[int, int]]) -> None:
    with open(dest_file_path, 'w') as f:
        for annotation in annotations:
            mapped_id = class_type_mapping[annotation.class_id] if class_type_mapping else annotation.class_id
            f.write(f"{mapped_id}, {annotation.box.x}, {annotation.box.y}, "
                    f"{annotation.box.x + annotation.box.w - 1}, {annotation.box.y + annotation.box.h - 1}\n")


def _single_image_annotations_to_voc(asset_id: str, attrs: Any, annotations: List[mirpb.Annotation],
                                     dest_file_path: str, cls_id_mgr: class_ids.ClassIdManager) -> None:
    # annotation
    annotation_node = ElementTree.Element('annotation')

    # annotation: folder
    folder_node = ElementTree.SubElement(annotation_node, 'folder')
    folder_node.text = 'folder'

    # annotation: filename
    filename_node = ElementTree.SubElement(annotation_node, 'filename')
    filename_node.text = asset_id

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

    # write to xml
    tree = ElementTree.ElementTree(annotation_node)
    tree.write(dest_file_path, encoding='utf-8')
