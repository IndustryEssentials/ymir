"""
exports the assets and annotations from mir format to ark-training-format
"""

from typing import Dict, List, Set

from mir.tools import data_reader, data_writer, revs_parser


def check_support_format(anno_format: str) -> bool:
    return anno_format in support_format_type()


def support_format_type() -> List[str]:
    return [f.value for f in data_writer.ExportFormat]


def format_type_from_str(anno_format: str) -> data_writer.ExportFormat:
    return data_writer.ExportFormat(anno_format.lower())


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
           format_type: data_writer.ExportFormat,
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
    rev_tid = revs_parser.TypRevTid()
    rev_tid.rev = base_branch
    rev_tid.tid = base_task_id

    dr = data_reader.MirDataReader(mir_root=mir_root,
                                   typ_rev_tid=rev_tid,
                                   asset_ids=asset_ids,
                                   class_ids=set(class_type_ids.keys()))
    dw = data_writer.RawDataWriter(mir_root=mir_root,
                                   assets_location=assets_location,
                                   assets_dir=asset_dir,
                                   annotations_dir=annotation_dir,
                                   need_ext=need_ext,
                                   need_id_sub_folder=need_id_sub_folder,
                                   overwrite=False,
                                   class_ids_mapping=class_type_ids,
                                   format_type=format_type,
                                   index_file_path=index_file_path,
                                   index_assets_prefix=index_assets_prefix,
                                   index_annotations_prefix=index_annotations_prefix)
    for asset_id, attrs, annotations in dr.read():
        dw.write(asset_id=asset_id, attrs=attrs, annotations=annotations)
    dw.close()

    return True


def export_lmdb(mir_root: str,
                assets_location: str,
                class_type_ids: Dict[int, int],
                asset_ids: Set[str],
                base_branch: str,
                base_task_id: str,
                format_type: data_writer.ExportFormat,
                lmdb_dir: str,
                index_file_path: str = '') -> bool:
    """
    export assets and annotations and pack them to lmdb format

    Args:
        mir_root (str): path to mir repo root directory
        assets_location (str): path to assets storage directory
        class_type_ids (Dict[int, int]): class ids (and it's mapping value)
            all objects within this dict keys will be exported, if None, export everything;
        asset_ids (Set[str]): export asset ids
        base_branch (str): data branch
        format_type (ExportFormat): format type, NONE means exports no annotations
        lmdb_dir: lmdb file directory
        index_file_path (str): path to index file, if None, generates no index file

    Raises:
        MirRuntimeError

    Returns:
        bool: returns True if success
    """
    rev_tid = revs_parser.TypRevTid()
    rev_tid.rev = base_branch
    rev_tid.tid = base_task_id

    dr = data_reader.MirDataReader(mir_root=mir_root,
                                   typ_rev_tid=rev_tid,
                                   asset_ids=asset_ids,
                                   class_ids=set(class_type_ids.keys()))
    dw = data_writer.LmdbDataWriter(mir_root=mir_root,
                                    assets_location=assets_location,
                                    lmdb_dir=lmdb_dir,
                                    class_ids_mapping=class_type_ids,
                                    format_type=format_type,
                                    index_file_path=index_file_path)
    for asset_id, attrs, annotations in dr.read():
        dw.write(asset_id=asset_id, attrs=attrs, annotations=annotations)
    dw.close()

    return True
