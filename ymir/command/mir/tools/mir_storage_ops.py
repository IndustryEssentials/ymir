import os
import time
from typing import Any, List, Dict, Optional, Set, Tuple

import fasteners  # type: ignore
from google.protobuf import json_format

from mir import scm
from mir.commands.checkout import CmdCheckout
from mir.commands.commit import CmdCommit
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import context, exodus, mir_storage, mir_repo_utils, revs_parser, settings as mir_settings
from mir.tools.code import MirCode
from mir.tools.errors import MirError, MirRuntimeError
import yaml


class MirStorageDatas:
    def __init__(self) -> None:
        self.mir_metadatas: Any = None
        self.mir_annotations: Any = None
        self.mir_keywords: Any = None
        self.mir_tasks: Any = None


class MirStorageOps():
    # private: save and load
    @classmethod
    def __save(cls, mir_root: str, mir_datas: Dict['mirpb.MirStorage.V', Any]) -> None:
        # add default members
        mir_tasks: mirpb.MirTasks = mir_datas[mirpb.MirStorage.MIR_TASKS]
        if mirpb.MirStorage.MIR_METADATAS not in mir_datas:
            mir_datas[mirpb.MirStorage.MIR_METADATAS] = mirpb.MirMetadatas()
        if mirpb.MirStorage.MIR_ANNOTATIONS not in mir_datas:
            mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS] = mirpb.MirAnnotations()

        mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]
        build_annotations_head_task_id(mir_annotations=mir_annotations, head_task_id=mir_tasks.head_task_id)

        # gen mir_keywords
        mir_keywords: mirpb.MirKeywords = mirpb.MirKeywords()
        build_mir_keywords(single_task_annotations=mir_annotations.task_annotations[mir_annotations.head_task_id],
                           mir_keywords=mir_keywords)
        mir_datas[mirpb.MirStorage.MIR_KEYWORDS] = mir_keywords

        # gen mir_context
        project_class_ids = context.load(mir_root=mir_root)
        mir_context = mirpb.MirContext()
        build_mir_context(mir_metadatas=mir_datas[mirpb.MirStorage.MIR_METADATAS],
                          mir_annotations=mir_annotations,
                          mir_keywords=mir_keywords,
                          project_class_ids=project_class_ids,
                          mir_context=mir_context)
        mir_datas[mirpb.MirStorage.MIR_CONTEXT] = mir_context

        # save to file
        for ms, mir_data in mir_datas.items():
            mir_file_path = os.path.join(mir_root, mir_storage.mir_path(ms))
            with open(mir_file_path, "wb") as m_f:
                m_f.write(mir_data.SerializeToString())

    @classmethod
    def __add_git_tag(cls, mir_root: str, tag: str) -> None:
        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        repo_git.tag(tag)

    # public: save and load
    @classmethod
    def save_and_commit(cls, mir_root: str, mir_branch: str, task_id: str, his_branch: Optional[str], mir_datas: dict,
                        commit_message: str) -> int:
        """
        saves and commit all contents in mir_datas to branch: `mir_branch`;
        branch will be created if not exists, and it's history will be after `his_branch`

        Args:
            mir_root (str): path to mir repo
            mir_branch (str): branch you wish to save to, if not exists, create new one
            task_id (str): task id for this commit
            his_branch (Optional[str]): if `mir_branch` not exists, this is the branch where you wish to start with
            mir_datas (Dict[mirpb.MirStorage.V, pb_message.Message]): datas you wish to save, need no mir_keywords,
                mir_tasks is needed, if mir_metadatas and mir_annotations not provided, they will be created as empty
                 datasets
            commit_message (str): commit messages

        Raises:
            MirRuntimeError

        Returns:
            int: result code
        """
        if not mir_root:
            mir_root = '.'
        if not commit_message:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty commit message")
        if not mir_branch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty mir branch")
        if not task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty task id')
        if mirpb.MirStorage.MIR_KEYWORDS in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_keywords')
        if mirpb.MirStorage.MIR_CONTEXT in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_context')
        if mirpb.MirStorage.MIR_TASKS not in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need mir_tasks')

        mir_tasks: mirpb.MirTasks = mir_datas[mirpb.MirStorage.MIR_TASKS]
        if task_id != mir_tasks.head_task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"head task id mismatch: {mir_tasks.head_task_id} != {task_id}")

        branch_exists = mir_repo_utils.mir_check_branch_exists(mir_root=mir_root, branch=mir_branch)
        if not branch_exists and not his_branch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_BRANCH_OR_TAG,
                                  error_message=f"branch {mir_branch} not exists, and his_branch not provided")

        # checkout to proper branch
        # if mir_branch exists, checkout mir_branch
        # if not exists, checkout his_branch, and checkout -b mir_branch
        if branch_exists:
            his_branch = mir_branch

        lock = fasteners.InterProcessLock(os.path.join(mir_root, '.mir_lock'))
        with lock:
            # checkout to his branch
            # cmd checkout also checks whether current branch is clean
            return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=str(his_branch), branch_new=False)
            if return_code != MirCode.RC_OK:
                return return_code

            # create dest_branch if not exists
            if not branch_exists:
                return_code = CmdCheckout.run_with_args(mir_root=mir_root, commit_id=mir_branch, branch_new=True)
                if return_code != MirCode.RC_OK:
                    return return_code

            cls.__save(mir_root=mir_root, mir_datas=mir_datas)

            ret_code = CmdCommit.run_with_args(mir_root=mir_root, msg=commit_message)
            if ret_code != MirCode.RC_OK:
                return ret_code

            # also have a tag for this commit
            cls.__add_git_tag(mir_root=mir_root, tag=revs_parser.join_rev_tid(mir_branch, task_id))

        return ret_code

    @classmethod
    def load(cls,
             mir_root: str,
             mir_branch: str,
             mir_storages: List['mirpb.MirStorage.V'],
             mir_task_id: str = '',
             as_dict: bool = False) -> Dict['mirpb.MirStorage.V', Any]:
        ret = {}
        for ms in mir_storages:
            ret[ms] = cls.load_single(mir_root=mir_root,
                                      mir_branch=mir_branch,
                                      mir_task_id=mir_task_id,
                                      ms=ms,
                                      as_dict=as_dict)
        return ret

    @classmethod
    def load_single(cls,
                    mir_root: str,
                    mir_branch: str,
                    ms: 'mirpb.MirStorage.V',
                    mir_task_id: str = '',
                    as_dict: bool = False) -> Any:
        rev = revs_parser.join_rev_tid(mir_branch, mir_task_id)

        mir_pb_type = mir_storage.mir_type(ms)
        mir_storage_data = mir_pb_type()
        mir_storage_data.ParseFromString(exodus.read_mir(mir_root=mir_root, rev=rev,
                                                         file_name=mir_storage.mir_path(ms)))

        if as_dict:
            mir_storage_data = json_format.MessageToDict(mir_storage_data,
                                                         preserving_proto_field_name=True,
                                                         use_integers_for_enums=True,
                                                         including_default_value_fields=True)

        return mir_storage_data

    @classmethod
    def load_single_model(cls, mir_root: str, mir_branch: str, mir_task_id: str = '') -> dict:
        mir_storage_data: mirpb.MirTasks = cls.load_single(mir_root=mir_root,
                                                           mir_branch=mir_branch,
                                                           ms=mirpb.MirStorage.MIR_TASKS,
                                                           mir_task_id=mir_task_id,
                                                           as_dict=False)

        task = mir_storage_data.tasks[mir_storage_data.head_task_id]
        if not task.model.model_hash:
            raise MirError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="no model")

        single_model_dict = json_format.MessageToDict(task.model,
                                                      preserving_proto_field_name=True,
                                                      use_integers_for_enums=True,
                                                      including_default_value_fields=True)
        single_model_dict[mir_settings.TASK_CONTEXT_PARAMETERS_KEY] = task.task_parameters
        single_model_dict[mir_settings.EXECUTOR_CONFIG_KEY] = yaml.safe_load(task.args).get(
            mir_settings.EXECUTOR_CONFIG_KEY, {}) if task.args else {}
        return single_model_dict

    @classmethod
    def load_branch_contents(cls,
                             mir_root: str,
                             mir_branch: str,
                             mir_task_id: str = '') -> Tuple[dict, dict, dict, dict, dict]:
        mir_storage_data = cls.load(mir_root=mir_root,
                                    mir_branch=mir_branch,
                                    mir_task_id=mir_task_id,
                                    mir_storages=mir_storage.get_all_mir_storage(),
                                    as_dict=True)
        return (mir_storage_data[mirpb.MirStorage.MIR_METADATAS], mir_storage_data[mirpb.MirStorage.MIR_ANNOTATIONS],
                mir_storage_data[mirpb.MirStorage.MIR_KEYWORDS], mir_storage_data[mirpb.MirStorage.MIR_TASKS],
                mir_storage_data[mirpb.MirStorage.MIR_CONTEXT])


# public: presave actions
def build_annotations_head_task_id(mir_annotations: mirpb.MirAnnotations, head_task_id: str) -> None:
    task_annotations_count = len(mir_annotations.task_annotations)
    if task_annotations_count == 0:
        mir_annotations.task_annotations[head_task_id].CopyFrom(mirpb.SingleTaskAnnotations())
    elif task_annotations_count == 1:
        task_id = list(mir_annotations.task_annotations.keys())[0]
        if task_id != head_task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message=f"annotation head task id mismatch: {head_task_id} != {task_id}")
    elif task_annotations_count > 1:
        # * now we allows only one task id in each mir_annotations
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_REPO,
                              error_message='more then one task ids found in mir_annotations')

    mir_annotations.head_task_id = head_task_id


def update_mir_tasks(mir_tasks: mirpb.MirTasks,
                     task_type: 'mirpb.TaskType.V',
                     task_id: str,
                     message: str,
                     unknown_types: Dict[str, int] = {},
                     model_hash: str = '',
                     model_mAP: float = 0,
                     return_code: int = 0,
                     return_msg: str = '',
                     args: str = '',
                     task_parameters: str = '') -> None:
    task: mirpb.Task = mirpb.Task()
    task.type = task_type
    task.name = message
    task.task_id = task_id
    task.timestamp = int(time.time())

    for k, v in unknown_types.items():
        task.unknown_types[k] = v

    task.model.model_hash = model_hash
    task.model.mean_average_precision = model_mAP
    task.return_code = return_code
    task.return_msg = return_msg
    task.args = args
    task.task_parameters = task_parameters

    task.ancestor_task_id = mir_tasks.head_task_id
    mir_tasks.tasks[task.task_id].CopyFrom(task)
    mir_tasks.head_task_id = task.task_id


def build_mir_keywords(single_task_annotations: mirpb.SingleTaskAnnotations, mir_keywords: mirpb.MirKeywords) -> None:
    """
    build mir_keywords from single_task_annotations

    Args:
        single_task_annotations (mirpb.SingleTaskAnnotations)
        mir_keywords (mirpb.MirKeywords)
    """
    # build mir_keywords.keywords
    for asset_id, single_image_annotations in single_task_annotations.image_annotations.items():
        mir_keywords.keywords[asset_id].predifined_keyids[:] = set(
            [annotation.class_id for annotation in single_image_annotations.annotations])

    # build mir_keywords.index_predifined_keyids
    mir_keywords.index_predifined_keyids.clear()

    for asset_id, keywords in mir_keywords.keywords.items():
        for key_id in keywords.predifined_keyids:
            mir_keywords.index_predifined_keyids[key_id].asset_ids.append(asset_id)

    # Remove redundant index values and sort
    for key_id, assets in mir_keywords.index_predifined_keyids.items():
        mir_keywords.index_predifined_keyids[key_id].asset_ids[:] = set(
            mir_keywords.index_predifined_keyids[key_id].asset_ids)


def build_mir_context(mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                      mir_keywords: mirpb.MirKeywords, project_class_ids: List[int],
                      mir_context: mirpb.MirContext) -> None:
    for key_id, assets in mir_keywords.index_predifined_keyids.items():
        mir_context.predefined_keyids_cnt[key_id] = len(assets.asset_ids)

    # project_predefined_keyids_cnt: assets count for project class ids
    #   suppose we have: 13 images for key 5, 15 images for key 6, and proejct_class_ids = [3, 5]
    #   project_predefined_keyids_cnt should be: {3: 0, 5: 13}
    project_positive_asset_ids: Set[str] = set()
    for key_id in project_class_ids:
        if key_id in mir_context.predefined_keyids_cnt:
            mir_context.project_predefined_keyids_cnt[key_id] = mir_context.predefined_keyids_cnt[key_id]
            project_positive_asset_ids.update(mir_keywords.index_predifined_keyids[key_id].asset_ids)
        else:
            mir_context.project_predefined_keyids_cnt[key_id] = 0

    # image_cnt, negative_images_cnt, project_negative_images_cnt
    mir_context.images_cnt = len(mir_metadatas.attributes)
    mir_context.negative_images_cnt = mir_context.images_cnt - len(
        mir_annotations.task_annotations[mir_annotations.head_task_id].image_annotations)
    if project_class_ids:
        mir_context.project_negative_images_cnt = mir_context.images_cnt - len(project_positive_asset_ids)
        # if no project_class_ids, project_negative_images_cnt set to 0
