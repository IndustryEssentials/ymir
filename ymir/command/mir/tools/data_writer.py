from enum import Enum
import os
from typing import List

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


class AnnotationFormat(str, Enum):
    AF_NONE = 'none'
    AF_ARK = 'ark'
    AF_VOC = 'voc'
    AF_LS_JSON = 'ls_json'


class BaseDataWriter:
    def __init__(self, assets_location: str) -> None:
        if not assets_location:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='empty assets_location')

        self._assets_location = assets_location
        self._unknown_format_count = 0  # count for assets with unknown format

    @property
    def unknown_format_count(self) -> int:
        return self._unknown_format_count


class RawDataWriter(BaseDataWriter):
    def __init__(self,
                 assets_location: str,
                 assets_dir: str,
                 annotations_dir: str,
                 need_ext: bool,
                 need_id_sub_folder: bool,
                 format_type: AnnotationFormat,
                 index_file_path: str = '',
                 index_assets_prefix: str = '',
                 index_annotations_prefix: str = '') -> None:
        """
        Args:
            assets_location (str): path to assets storage directory
            assets_dir (str): export asset directory
            annotations_dir (str): export annotation directory, if format_type is NO_ANNOTATION, this could be None
            need_ext (bool): if true, all export assets will have it's type as ext, jpg, png, etc.
            need_id_sub_folder (bool): if True, use last 2 chars of asset id as a sub folder name
            format_type (ExportFormat): format type, NONE means exports no annotations
            index_file_path (str): path to index file, if None, generates no index file
            index_assets_prefix (str): prefix path added to each asset index path
            index_annotations_prefix (str): prefix path added to each annotation index path
        """
        super().__init__(assets_location=assets_location)

        if not assets_dir or not annotations_dir:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='empty assets_dir or annotations_dir')

        # prepare out dirs
        os.makedirs(assets_dir, exist_ok=True)
        os.makedirs(annotations_dir, exist_ok=True)
        if index_file_path:
            os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

        self._assets_dir = assets_dir
        self._annotations_dir = annotations_dir
        self._need_ext = need_ext
        self._need_id_sub_folder = need_id_sub_folder
        self._format_type = format_type
        self._index_file_path = index_file_path
        self._index_assets_prefix = index_assets_prefix
        self._index_annotations_prefix = index_annotations_prefix

    def write(self, asset_id: str, attr: mirpb.MetadataAttributes, annotations: List[mirpb.Annotation]) -> None:
        # write asset
        # write annotation file
        pass


class LmdbDataWriter(BaseDataWriter):
    def __init__(self,
                 assets_location: str,
                 lmdb_dir: str,
                 format_type: AnnotationFormat,
                 index_file_path: str = '') -> None:
        super().__init__(assets_location=assets_location)

    def write(self, asset_id: str, attr: mirpb.MetadataAttributes, annotations: List[mirpb.Annotation]) -> None:
        # write asset
        # write annotation
        pass
