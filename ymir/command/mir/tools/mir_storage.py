from typing import Any, List

from mir.protos import mir_command_pb2 as mirpb


MIR_ASSOCIATED_FILES = ['.git', '.mir', '.gitignore', '.mir_lock']


def mir_type(mir_storage: 'mirpb.MirStorage.V') -> Any:
    MIR_TYPE = {
        mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas,
        mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations,
        mirpb.MirStorage.MIR_KEYWORDS: mirpb.MirKeywords,
        mirpb.MirStorage.MIR_TASKS: mirpb.MirTasks,
        mirpb.MirStorage.MIR_CONTEXT: mirpb.MirContext,
    }
    return MIR_TYPE[mir_storage]


def mir_path(mir_storage: 'mirpb.MirStorage.V') -> str:
    MIR_PATH = {
        mirpb.MirStorage.MIR_METADATAS: 'metadatas.mir',
        mirpb.MirStorage.MIR_ANNOTATIONS: 'annotations.mir',
        mirpb.MirStorage.MIR_KEYWORDS: 'keywords.mir',
        mirpb.MirStorage.MIR_TASKS: 'tasks.mir',
        mirpb.MirStorage.MIR_CONTEXT: 'context.mir',
    }
    return MIR_PATH[mir_storage]


def mir_attr_name(mir_storage: 'mirpb.MirStorage.V') -> str:
    MIR_STORAGE_TO_ATTR_NAME = {
        mirpb.MirStorage.MIR_METADATAS: 'mir_metadatas',
        mirpb.MirStorage.MIR_ANNOTATIONS: 'mir_annotations',
        mirpb.MirStorage.MIR_KEYWORDS: 'mir_keywords',
        mirpb.MirStorage.MIR_TASKS: 'mir_tasks',
        mirpb.MirStorage.MIR_CONTEXT: 'mir_context',
    }
    return MIR_STORAGE_TO_ATTR_NAME[mir_storage]


def get_all_mir_paths() -> List[str]:
    return [mir_path(ms) for ms in get_all_mir_storage()]


def get_all_mir_storage() -> List['mirpb.MirStorage.V']:
    return [
        mirpb.MirStorage.MIR_METADATAS,
        mirpb.MirStorage.MIR_ANNOTATIONS,
        mirpb.MirStorage.MIR_KEYWORDS,
        mirpb.MirStorage.MIR_TASKS,
        mirpb.MirStorage.MIR_CONTEXT,
    ]
