from typing import Any, List, Dict

from google.protobuf import json_format

from mir.tools import exodus, revs_parser

from mir.protos import mir_command_110_pb2 as mirpb


class MirStorageOps():
    # public: save and load
    @classmethod
    def load_single_storage(cls,
                            mir_root: str,
                            mir_branch: str,
                            ms: 'mirpb.MirStorage.V',
                            mir_task_id: str = '',
                            as_dict: bool = False) -> Any:
        rev = revs_parser.join_rev_tid(mir_branch, mir_task_id)

        mir_pb_type = _mir_type(ms)
        mir_storage_data = mir_pb_type()
        mir_storage_data.ParseFromString(exodus.read_mir(mir_root=mir_root, rev=rev,
                                                         file_name=_mir_path(ms)))

        if as_dict:
            mir_storage_data = cls.__message_to_dict(mir_storage_data)

        return mir_storage_data

    @classmethod
    def load_multiple_storages(cls,
                               mir_root: str,
                               mir_branch: str,
                               ms_list: List['mirpb.MirStorage.V'],
                               mir_task_id: str = '',
                               as_dict: bool = False) -> List[Any]:
        return [
            cls.load_single_storage(
                mir_root=mir_root,
                mir_branch=mir_branch,
                ms=ms,
                mir_task_id=mir_task_id,
                as_dict=as_dict,
            ) for ms in ms_list
        ]

    @classmethod
    def __message_to_dict(cls, message: Any) -> Dict:
        return json_format.MessageToDict(message,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True,
                                         including_default_value_fields=True)


def _mir_type(ms: 'mirpb.MirStorage.V') -> Any:
    MIR_TYPE = {
        mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations,
        mirpb.MirStorage.MIR_KEYWORDS: mirpb.MirKeywords,
        mirpb.MirStorage.MIR_TASKS: mirpb.MirTasks,
        mirpb.MirStorage.MIR_CONTEXT: mirpb.MirContext,
    }
    return MIR_TYPE[ms]


def _mir_path(ms: 'mirpb.MirStorage.V') -> str:
    MIR_PATH = {
        mirpb.MirStorage.MIR_METADATAS: 'metadatas.mir',
        mirpb.MirStorage.MIR_ANNOTATIONS: 'annotations.mir',
        mirpb.MirStorage.MIR_KEYWORDS: 'keywords.mir',
        mirpb.MirStorage.MIR_TASKS: 'tasks.mir',
        mirpb.MirStorage.MIR_CONTEXT: 'context.mir',
    }
    return MIR_PATH[ms]


def get_all_mir_paths() -> List[str]:
    return [_mir_path(ms) for ms in get_all_mir_storage()]


def get_all_mir_storage() -> List['mirpb.MirStorage.V']:
    return [
        mirpb.MirStorage.MIR_METADATAS,
        mirpb.MirStorage.MIR_ANNOTATIONS,
        mirpb.MirStorage.MIR_KEYWORDS,
        mirpb.MirStorage.MIR_TASKS,
        mirpb.MirStorage.MIR_CONTEXT,
    ]
