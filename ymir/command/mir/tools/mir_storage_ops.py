import os
from typing import Any, List, Dict, Optional

import fasteners  # type: ignore
from google.protobuf import json_format

from mir import scm
from mir.commands.checkout import CmdCheckout
from mir.commands.commit import CmdCommit
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import exodus, mir_storage, mir_repo_utils, revs_parser
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError


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
            empty_mir_annotations = mirpb.MirAnnotations()
            empty_mir_annotations.task_annotations[mir_tasks.head_task_id]  # empty task_annotation
            mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS] = empty_mir_annotations

        # gen mir_keywords
        mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]
        mir_keywords: mirpb.MirKeywords = mirpb.MirKeywords()
        build_annotations_head_task_id(mir_annotations=mir_annotations)
        generate_keywords_cis(
            single_task_annotations=mir_annotations.task_annotations[mir_annotations.head_task_id],
            mir_keywords=mir_keywords)
        build_keywords_index(mir_keywords=mir_keywords)
        mir_datas[mirpb.MirStorage.MIR_KEYWORDS] = mir_keywords

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
    def save_and_commit(cls, mir_root: str, mir_branch: str, task_id: str, his_branch: Optional[str],
                        mir_datas: Dict['mirpb.MirStorage.V', Any], commit_message: str) -> int:
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
        if mirpb.MirStorage.MIR_TASKS not in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='invalid mir_tasks')

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
        with exodus.open_mir(mir_root=mir_root, file_name=mir_storage.mir_path(ms), rev=rev, mode="rb") as f:
            mir_storage_data.ParseFromString(f.read())

        if as_dict:
            mir_storage_data = json_format.MessageToDict(mir_storage_data,
                                                         preserving_proto_field_name=True,
                                                         use_integers_for_enums=True,
                                                         including_default_value_fields=True)

        return mir_storage_data


# public: presave actions
def build_keywords_index(mir_keywords: mirpb.MirKeywords) -> int:
    if not mir_keywords:
        raise RuntimeError("Invalid mir_keywords")

    mir_keywords.predifined_keyids_cnt.clear()
    mir_keywords.customized_keywords_cnt.clear()
    mir_keywords.index_predifined_keyids.clear()

    for asset_id, keywords in mir_keywords.keywords.items():
        for key_id in keywords.predifined_keyids:
            mir_keywords.predifined_keyids_cnt[key_id] += 1
            mir_keywords.index_predifined_keyids[key_id].asset_ids.append(asset_id)
        for keyword in keywords.customized_keywords:
            mir_keywords.customized_keywords_cnt[keyword] += 1

    mir_keywords.predifined_keyids_total = 0
    for cnt in mir_keywords.predifined_keyids_cnt.values():
        mir_keywords.predifined_keyids_total += cnt
    mir_keywords.customized_keywords_total = 0
    for cnt in mir_keywords.customized_keywords_cnt.values():
        mir_keywords.customized_keywords_total += cnt

    # Remove redundant index values.
    for key_id, assets in mir_keywords.index_predifined_keyids.items():
        mir_keywords.index_predifined_keyids[key_id].asset_ids[:] = set(
            mir_keywords.index_predifined_keyids[key_id].asset_ids)

    return MirCode.RC_OK


def build_annotations_head_task_id(mir_annotations: mirpb.MirAnnotations) -> None:
    task_ids = list(mir_annotations.task_annotations.keys())
    if len(task_ids) == 1:
        mir_annotations.head_task_id = task_ids[0]
    elif len(task_ids) > 1:
        # * now we allows only one task id in each mir_annotations
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_MIR_FILE,
                              error_message=f'more then one task ids found in mir_annotations: {task_ids}')


def add_mir_task(mir_tasks: mirpb.MirTasks, task: mirpb.Task) -> None:
    """
    add `task` to `mir_tasks`

    Args:
        mir_tasks (mirpb.MirTasks): contents in tasks.mir from repo
        task (mirpb.Task): new task you wish to add

    Raises:
        MirRuntimeError: if `task` has no task_id
        MirRuntimeError: if `task.task_id` already exists
    """
    if not task.task_id:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty task id')
    if task.task_id in mir_tasks.tasks:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_BRANCH_OR_TAG,
                              error_message=f"tasl id {task.task_id} already exists")

    orig_head_task_id = mir_tasks.head_task_id
    task.ancestor_task_id = orig_head_task_id
    mir_tasks.tasks[task.task_id].CopyFrom(task)
    mir_tasks.head_task_id = task.task_id


def generate_keywords_cis(single_task_annotations: mirpb.SingleTaskAnnotations,
                          mir_keywords: mirpb.MirKeywords) -> None:
    """
    generate mir_keywords's keyids from single_task_annotations

    Args:
        single_task_annotations (mirpb.SingleTaskAnnotations)
        mir_keywords (mirpb.MirKeywords)
    """
    for asset_id, single_image_annotations in single_task_annotations.image_annotations.items():
        mir_keywords.keywords[asset_id].predifined_keyids[:] = set(
            [annotation.class_id for annotation in single_image_annotations.annotations])
