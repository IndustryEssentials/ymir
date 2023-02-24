from functools import reduce
from math import ceil
import os
import time
from typing import Any, List, Dict, Optional

import fasteners  # type: ignore
from google.protobuf import json_format

from mir import scm
from mir.commands.checkout import CmdCheckout
from mir.commands.commit import CmdCommit
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import exodus
from mir.tools import mir_storage, mir_repo_utils, revs_parser
from mir.tools import settings as mir_settings
from mir.tools.annotations import valid_image_annotation
from mir.tools.code import MirCode, time_it
from mir.tools.errors import MirRuntimeError
from mir.tools.eval import eval_ops


def create_evaluate_config(is_instance_segmentation: bool = False,
                           conf_thr: float = mir_settings.DEFAULT_EVALUATE_CONF_THR,
                           iou_thrs: str = mir_settings.DEFAULT_EVALUATE_IOU_THR,
                           need_pr_curve: bool = False,
                           class_ids: List[int] = []) -> mirpb.EvaluateConfig:
    evaluate_config = mirpb.EvaluateConfig()
    evaluate_config.conf_thr = conf_thr
    evaluate_config.iou_thrs_interval = iou_thrs
    evaluate_config.need_pr_curve = need_pr_curve
    evaluate_config.class_ids[:] = class_ids
    evaluate_config.is_instance_segmentation = is_instance_segmentation
    return evaluate_config


class MirStorageOps():
    # private: save and load
    @classmethod
    def __build_task_keyword_context(cls, mir_datas: Dict['mirpb.MirStorage.V', Any], task: mirpb.Task,
                                     evaluate_config: Optional[mirpb.EvaluateConfig]) -> None:
        # add default members and check pred/gt object type
        mir_metadatas: mirpb.MirMetadatas = mir_datas[mirpb.MirStorage.MIR_METADATAS]
        mir_annotations: mirpb.MirAnnotations = mir_datas[mirpb.MirStorage.MIR_ANNOTATIONS]
        invalid_asset_ids = {
            k
            for k, v in mir_annotations.prediction.image_annotations.items()
            if not valid_image_annotation(v)
        }
        for asset_id in invalid_asset_ids:
            del mir_annotations.prediction.image_annotations[asset_id]
        invalid_asset_ids = {
            k
            for k, v in mir_annotations.ground_truth.image_annotations.items()
            if not valid_image_annotation(v)
        }
        for asset_id in invalid_asset_ids:
            del mir_annotations.ground_truth.image_annotations[asset_id]
        mir_annotations.prediction.task_id = task.task_id
        mir_annotations.ground_truth.task_id = task.task_id
        if mirpb.ObjectType.OT_UNKNOWN in {mir_annotations.prediction.type, mir_annotations.ground_truth.type}:
            raise MirRuntimeError(
                error_message=f"Can not save annotations with unknown object type, task id: {task.task_id}, "
                f"pred type: {mir_annotations.prediction.type}, gt type: {mir_annotations.ground_truth.type}",
                error_code=MirCode.RC_CMD_INVALID_OBJECT_TYPE)

        # build mir_tasks
        mir_tasks: mirpb.MirTasks = mirpb.MirTasks()
        mir_tasks.head_task_id = task.task_id
        mir_tasks.tasks[mir_tasks.head_task_id].CopyFrom(task)

        if not evaluate_config:
            evaluate_config = create_evaluate_config(
                is_instance_segmentation=mir_annotations.prediction.is_instance_segmentation)

        evaluation = eval_ops.evaluate_with_pb(
            prediction=mir_annotations.prediction,
            ground_truth=mir_annotations.ground_truth,
            config=evaluate_config,
            assets_metadata=mir_metadatas,
        )
        mir_tasks.tasks[mir_tasks.head_task_id].evaluation.CopyFrom(evaluation)

        mir_datas[mirpb.MirStorage.MIR_TASKS] = mir_tasks

        # gen mir_keywords
        mir_keywords: mirpb.MirKeywords = mirpb.MirKeywords()
        cls.__build_mir_keywords_ci_tag(task_annotations=mir_annotations.prediction,
                                        keyword_to_index=mir_keywords.pred_idx)
        cls.__build_mir_keywords_ci_tag(task_annotations=mir_annotations.ground_truth,
                                        keyword_to_index=mir_keywords.gt_idx)
        # ck to assets
        for asset_id, image_cks in mir_annotations.image_cks.items():
            for k, v in image_cks.cks.items():
                mir_keywords.ck_idx[k].asset_annos[asset_id]  # empty record to asset id
                mir_keywords.ck_idx[k].sub_indexes[v].key_ids[asset_id]  # empty record to asset id
        mir_datas[mirpb.MirStorage.MIR_KEYWORDS] = mir_keywords

        # gen mir_context
        mir_context = mirpb.MirContext()
        cls.__build_mir_context(mir_metadatas=mir_metadatas,
                                mir_annotations=mir_annotations,
                                mir_keywords=mir_keywords,
                                mir_context=mir_context)
        mir_datas[mirpb.MirStorage.MIR_CONTEXT] = mir_context

    @classmethod
    @time_it
    def __build_mir_keywords_ci_tag(cls, task_annotations: mirpb.SingleTaskAnnotations,
                                    keyword_to_index: mirpb.CiTagToIndex) -> None:
        task_cis = set()
        for asset_id, single_image_annotations in task_annotations.image_annotations.items():
            image_cis = set()
            for annotation in single_image_annotations.boxes:
                image_cis.add(annotation.class_id)
                # ci to annos
                keyword_to_index.cis[annotation.class_id].key_ids[asset_id].ids.append(annotation.index)

                # tags to annos
                for k, v in annotation.tags.items():
                    keyword_to_index.tags[k].asset_annos[asset_id].ids.append(annotation.index)
                    keyword_to_index.tags[k].sub_indexes[v].key_ids[asset_id].ids.append(annotation.index)

            single_image_annotations.img_class_ids[:] = image_cis
            task_cis.update(image_cis)

        task_annotations.task_class_ids[:] = task_cis

    @classmethod
    def __build_mir_context_stats(cls, anno_stats: mirpb.AnnoStats, mir_metadatas: mirpb.MirMetadatas,
                                  task_annotations: mirpb.SingleTaskAnnotations,
                                  keyword_to_index: mirpb.CiTagToIndex) -> None:
        image_annotations = task_annotations.image_annotations

        anno_stats.eval_class_ids[:] = task_annotations.eval_class_ids

        # anno_stats.asset_cnt
        anno_stats.positive_asset_cnt = len(image_annotations)
        anno_stats.negative_asset_cnt = len(mir_metadatas.attributes) - len(image_annotations)

        # anno_stats.class_ids_cnt, class_ids_obj_cnt and total_obj_cnt
        for ci, ci_assets in keyword_to_index.cis.items():
            anno_stats.class_ids_cnt[ci] = len(ci_assets.key_ids)
            anno_stats.class_ids_obj_cnt[ci] = sum([len(v.ids) for v in ci_assets.key_ids.values()])
        anno_stats.total_obj_cnt = sum(anno_stats.class_ids_obj_cnt.values())

        # anno_stats.tags_cnt
        for tag, tag_to_annos in keyword_to_index.tags.items():
            for anno_idxes in tag_to_annos.asset_annos.values():
                anno_stats.tags_cnt[tag].cnt += len(anno_idxes.ids)

            for sub_tag, sub_tag_to_annos in tag_to_annos.sub_indexes.items():
                for anno_idxes in sub_tag_to_annos.key_ids.values():
                    anno_stats.tags_cnt[tag].sub_cnt[sub_tag] += len(anno_idxes.ids)

        # anno_stats.class_ids_mask_area and anno_stats.total_mask_area
        for single_image_annotations in task_annotations.image_annotations.values():
            for object_annotation in single_image_annotations.boxes:
                anno_stats.class_ids_mask_area[object_annotation.class_id] += object_annotation.mask_area
        anno_stats.total_mask_area = sum(anno_stats.class_ids_mask_area.values())

    @classmethod
    @time_it
    def __build_mir_context(cls, mir_metadatas: mirpb.MirMetadatas, mir_annotations: mirpb.MirAnnotations,
                            mir_keywords: mirpb.MirKeywords, mir_context: mirpb.MirContext) -> None:
        mir_context.images_cnt = len(mir_metadatas.attributes)
        total_asset_bytes = reduce(lambda s, v: s + v.byte_size, mir_metadatas.attributes.values(), 0)
        mir_context.total_asset_mbytes = ceil(total_asset_bytes / mir_settings.BYTES_PER_MB)

        # cks cnt
        for ck, ck_assets in mir_keywords.ck_idx.items():
            mir_context.cks_cnt[ck].cnt = len(ck_assets.asset_annos)
            for sub_ck, sub_ck_to_assets in ck_assets.sub_indexes.items():
                mir_context.cks_cnt[ck].sub_cnt[sub_ck] = len(sub_ck_to_assets.key_ids)

        cls.__build_mir_context_stats(anno_stats=mir_context.pred_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.prediction,
                                      keyword_to_index=mir_keywords.pred_idx)
        cls.__build_mir_context_stats(anno_stats=mir_context.gt_stats,
                                      mir_metadatas=mir_metadatas,
                                      task_annotations=mir_annotations.ground_truth,
                                      keyword_to_index=mir_keywords.gt_idx)

    @classmethod
    def __add_git_tag(cls, mir_root: str, tag: str) -> None:
        repo_git = scm.Scm(root_dir=mir_root, scm_executable='git')
        repo_git.tag(tag)

    # public: save and load
    @classmethod
    def save_and_commit(cls,
                        mir_root: str,
                        mir_branch: str,
                        his_branch: Optional[str],
                        mir_datas: Dict,
                        task: mirpb.Task,
                        evaluate_config: Optional[mirpb.EvaluateConfig] = None) -> int:
        """
        saves and commit all contents in mir_datas to branch: `mir_branch`;
        branch will be created if not exists, and it's history will be after `his_branch`

        Args:
            mir_root (str): path to mir repo
            mir_branch (str): branch you wish to save to, if not exists, create new one
            his_branch (Optional[str]): if `mir_branch` not exists, this is the branch where you wish to start with
            mir_datas (Dict[mirpb.MirStorage.V, pb_message.Message]): datas you wish to save, need no mir_keywords,
                mir_tasks is needed, if mir_metadatas and mir_annotations not provided, they will be created as empty
                 datasets
            task (mirpb.Task): task for this commit
            evaluate_config (mirpb.EvaluateConfig): evaluate config

        Raises:
            MirRuntimeError

        Returns:
            int: result code
        """
        if not mir_root:
            mir_root = '.'
        if not mir_branch:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty mir branch")
        if mirpb.MirStorage.MIR_METADATAS not in mir_datas or mirpb.MirStorage.MIR_ANNOTATIONS not in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                                  error_message='need mir_metadatas and mir_annotations')
        if mirpb.MirStorage.MIR_KEYWORDS in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_keywords')
        if mirpb.MirStorage.MIR_CONTEXT in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_context')
        if mirpb.MirStorage.MIR_TASKS in mir_datas:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='need no mir_tasks')
        if not task.name:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message="empty commit message")
        if not task.task_id:
            raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message='empty task id')

        # Build all mir_datas.
        cls.__build_task_keyword_context(mir_datas=mir_datas,
                                         task=task,
                                         evaluate_config=evaluate_config)

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

            # save to file
            for ms, mir_data in mir_datas.items():
                mir_file_path = os.path.join(mir_root, mir_storage.mir_path(ms))
                with open(mir_file_path, "wb") as m_f:
                    m_f.write(mir_data.SerializeToString())

            ret_code = CmdCommit.run_with_args(mir_root=mir_root, msg=task.name)
            if ret_code != MirCode.RC_OK:
                return ret_code

            # also have a tag for this commit
            cls.__add_git_tag(mir_root=mir_root, tag=revs_parser.join_rev_tid(mir_branch, task.task_id))

        return ret_code

    # public: load
    @classmethod
    def load_single_storage(cls,
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

        # update object type
        if isinstance(mir_storage_data, mirpb.MirAnnotations):
            if mir_storage_data.prediction.type == mirpb.ObjectType.OT_UNKNOWN:
                mir_storage_data.prediction.type = mirpb.ObjectType.OT_NO_ANNOTATIONS
            if mir_storage_data.ground_truth.type == mirpb.ObjectType.OT_UNKNOWN:
                mir_storage_data.ground_truth.type = mirpb.ObjectType.OT_NO_ANNOTATIONS

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


def create_task_record(task_type: 'mirpb.TaskType.V',
                       task_id: str,
                       message: str,
                       new_types: Dict[str, int] = {},
                       new_types_added: bool = False,
                       return_code: int = 0,
                       return_msg: str = '',
                       serialized_executor_config: str = '',
                       executor: str = '',
                       model_meta: mirpb.ModelMeta = None,
                       evaluation: mirpb.Evaluation = None,
                       src_revs: str = '',
                       dst_rev: str = '') -> mirpb.Task:
    task_dict = {
        'type': task_type,
        'name': message,
        'task_id': task_id,
        'timestamp': int(time.time()),
        'return_code': return_code,
        'return_msg': return_msg,
        'serialized_executor_config': serialized_executor_config,
        'new_types': new_types,
        'new_types_added': new_types_added,
        'executor': executor,
        'src_revs': src_revs,
        'dst_rev': dst_rev,
    }
    task: mirpb.Task = mirpb.Task()
    json_format.ParseDict(task_dict, task)

    if model_meta:
        task.model.CopyFrom(model_meta)

    if evaluation:
        task.evaluation.CopyFrom(evaluation)

    return task
