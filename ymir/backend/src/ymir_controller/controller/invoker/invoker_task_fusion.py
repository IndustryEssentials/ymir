from typing import Dict, List, Optional, Tuple

from common_utils.labels import UserLabels
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import revs, utils
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


class TaskFusionInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if not request.in_dataset_ids:
            return utils.make_general_response(CTLResponseCode.ARG_VALIDATION_FAILED, 'empty in_dataset_ids')

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_fuse, 1.0)]

    @classmethod
    def subtask_invoke_fuse(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                            assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                            subtask_workdir: str, his_task_id: Optional[str],
                            in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        return cls.fuse_cmd(repo_root=repo_root,
                            task_id=subtask_id,
                            work_dir=subtask_workdir,
                            in_dataset_ids=request.in_dataset_ids,
                            ex_dataset_ids=request.ex_dataset_ids,
                            annotation_type=request.annotation_type,
                            merge_strategy=request.merge_strategy,
                            in_class_ids=request.in_class_ids,
                            ex_class_ids=request.ex_class_ids,
                            user_labels=user_labels,
                            sample_count=request.sampling_count,
                            sample_rate=request.sampling_rate)

    @classmethod
    def fuse_cmd(cls, repo_root: str, task_id: str, work_dir: str, in_dataset_ids: List[str], ex_dataset_ids: List[str],
                 merge_strategy: backend_pb2.MergeStrategy, in_class_ids: List[int], ex_class_ids: List[str],
                 annotation_type: mir_cmd_pb.AnnotationType, user_labels: UserLabels, sample_count: int,
                 sample_rate: float) -> backend_pb2.GeneralResp:
        # merge args
        fuse_cmd = [
            utils.mir_executable(), 'fuse', '--root', repo_root, '--dst-rev', f"{task_id}@{task_id}", '-w', work_dir,
            '--src-revs', revs.build_src_revs(in_src_revs=in_dataset_ids),
            '-s', backend_pb2.MergeStrategy.Name(merge_strategy).lower()
        ]
        if ex_dataset_ids:
            fuse_cmd.extend(['--ex-src-revs', revs.build_src_revs(in_src_revs=ex_dataset_ids)])

        # filter args
        if in_class_ids:
            fuse_cmd.extend(['--cis', ';'.join(user_labels.main_name_for_ids(class_ids=in_class_ids))])
        if ex_class_ids:
            fuse_cmd.extend(['--ex-cis', ';'.join(user_labels.main_name_for_ids(class_ids=ex_class_ids))])
        fuse_cmd.extend(['--user-label-file', user_labels.storage_file])
        fuse_cmd.extend(['--filter-anno-src', utils.annotation_type_str(annotation_type)])

        # sample args
        if sample_count:
            fuse_cmd.extend(['--count', f"{sample_count}"])
        elif sample_rate:
            fuse_cmd.extend(['--rate', f"{sample_rate}"])

        return utils.run_command(fuse_cmd)
