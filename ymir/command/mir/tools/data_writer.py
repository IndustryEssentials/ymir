from enum import Enum
import os
from typing import List

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


class AnnotationFormat(Enum, str):
    AF_NONE = 'none'
    AF_ARK = 'ark'
    AF_VOC = 'voc'
    AF_LS_JSON = 'ls_json'


class RawDataWriter:
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
        if not assets_location or not assets_dir or not annotations_dir:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='empty assets_location, assets_dir or annotations_dir')
        
        os.makedirs(assets_dir, exist_ok=True)
        os.makedirs(annotations_dir, exist_ok=True)

    def write(self, asset_id: str, attr: mirpb.MetadataAttributes, annotations: List[mirpb.Annotation]) -> None:
        pass


class LmdbDataWriter:
    def __init__(self,
                 assets_location: str,
                 lmdb_dir: str,
                 format_type: AnnotationFormat,
                 index_file_path: str = '') -> None:
        pass

    def write(self, asset_id: str, attr: mirpb.MetadataAttributes, annotations: List[mirpb.Annotation]) -> None:
        pass
