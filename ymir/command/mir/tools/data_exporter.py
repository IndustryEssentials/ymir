"""
exports the assets and annotations from mir format to ark-training-format
"""

from collections.abc import Collection
from enum import Enum
import logging
import os
from typing import Callable, Dict, List, Optional, Set

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, data_writer, mir_storage_ops
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


def _rel_annotation_path_for_asset(rel_asset_path: str, format_type: ExportFormat) -> str:
    rel_asset_path_without_ext = os.path.splitext(rel_asset_path)[0]
    return f"{rel_asset_path_without_ext}{format_file_ext(format_type)}"


def format_file_output_func(anno_format: ExportFormat) -> Callable:
    _format_func_map = {
        ExportFormat.EXPORT_FORMAT_ARK: data_writer._single_image_annotations_to_ark,
        ExportFormat.EXPORT_FORMAT_VOC: data_writer._single_image_annotations_to_voc,
        ExportFormat.EXPORT_FORMAT_LS_JSON: data_writer._single_image_annotations_to_ls_json,
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
           index_file_path: str = '',
           index_assets_prefix: str = '',
           index_annotations_prefix: str = '') -> bool:
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
        index_file_path (str): path to index file, if None, generates no index file
        index_assets_prefix (str): prefix path added to each asset index path
        index_annotations_prefix (str): prefix path added to each annotation index path

    Raises:
        MirRuntimeError

    Returns:
        bool: returns True if success
    """
    if not mir_root:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message="invalid mir_repo")

    if not check_support_format(format_type):
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"invalid --format: {format_type}")

    # export assets
    os.makedirs(asset_dir, exist_ok=True)
    asset_result = mir_utils.store_assets_to_dir(asset_ids=list(asset_ids),
                                                 out_root=asset_dir,
                                                 sub_folder=".",
                                                 asset_location=assets_location,
                                                 overwrite=False,
                                                 create_prefix=need_id_sub_folder,
                                                 need_suffix=need_ext)

    # export annotations
    if format_type != ExportFormat.EXPORT_FORMAT_NO_ANNOTATION:
        [mir_metadatas, mir_annotations] = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=base_branch,
            mir_task_id=base_task_id,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS])

        # add all annotations to assets_to_det_annotations_dict
        # key: asset_id as str, value: annotations as List[mirpb.Annotation]
        assets_to_det_annotations_dict = _annotations_by_assets(
            mir_annotations=mir_annotations,
            class_type_ids=set(class_type_ids.keys()) if class_type_ids else None,
            base_task_id=mir_annotations.head_task_id)

        _export_detect_annotations_to_path(asset_ids=list(asset_ids),
                                           format_type=format_type,
                                           mir_metadatas=mir_metadatas,
                                           annotations_dict=assets_to_det_annotations_dict,
                                           class_type_mapping=class_type_ids,
                                           dest_path=annotation_dir,
                                           mir_root=mir_root,
                                           assert_id_filename_map=asset_result)

    # generate index file
    if index_file_path:
        _generate_asset_index_file(asset_rel_paths=asset_result.values(),
                                   index_assets_prefix=index_assets_prefix,
                                   index_annotations_prefix=index_annotations_prefix,
                                   index_file_path=index_file_path,
                                   format_type=format_type)

    return True


def _generate_asset_index_file(asset_rel_paths: Collection,
                               index_assets_prefix: str,
                               index_annotations_prefix: str,
                               index_file_path: str,
                               format_type: ExportFormat,
                               overwrite: bool = True,
                               image_exts: tuple = ('.jpg', '.jpeg', '.png')) -> None:
    """
    generate index file for export result

    if format_type == NO_ANNOTATION, index file contains only asset paths

    if not, index file contains both asset and annotation paths, separated by `\t`

    Args:
        asset_rel_paths (Collection): the relative asset paths, element type: str
        index_assets_prefix (str): prefix path added in front of each element in asset_rel_paths
        index_annotations_prefix (str): prefix path added in front of each annotations
        index_file_path (str): index file save path
        format_type (ExporterFormat): format type
        override (bool): if True, override if file already exists, if False, raise Exception when already exists

    Raise:
        MirRuntimeError: if index file already exists, and override set to False
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

            asset_path = os.path.join(index_assets_prefix, item)
            if format_type == ExportFormat.EXPORT_FORMAT_NO_ANNOTATION:
                annotation_path = ''
            else:
                annotation_rel_path = _rel_annotation_path_for_asset(rel_asset_path=item, format_type=format_type)
                annotation_path = os.path.join(index_annotations_prefix, annotation_rel_path)
            f.write(f"{asset_path}\t{annotation_path}\n")


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
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
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
        asset_file_name = assert_id_filename_map[asset_id]
        anno_str = format_func(asset_id=asset_id,
                               attrs=attrs,
                               annotations=annotations,
                               class_type_mapping=class_type_mapping,
                               cls_id_mgr=cls_id_mgr,
                               asset_filename=asset_file_name)

        annotation_file_path = os.path.join(
            dest_path, _rel_annotation_path_for_asset(rel_asset_path=asset_file_name, format_type=format_type))
        os.makedirs(os.path.dirname(annotation_file_path), exist_ok=True)
        with open(annotation_file_path, 'w') as f:
            f.write(anno_str)

    logging.info(f"missing annotations: {missing_counter}, "
                 f"empty annotations: {empty_counter} out of {len(asset_ids)} assets")
