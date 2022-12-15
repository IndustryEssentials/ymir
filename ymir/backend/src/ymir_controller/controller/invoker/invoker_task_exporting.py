import os
from typing import Dict, List, Optional, Tuple
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


class TaskExportingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if len(request.in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid in_dataset_ids {request.in_dataset_ids}")

        exporting_request = request.req_create_task.exporting
        asset_dir = exporting_request.asset_dir
        if not asset_dir:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED, message="empty asset_dir")
        os.makedirs(asset_dir, exist_ok=True)

        if exporting_request.format != mir_cmd_pb.ExportFormat.EF_NO_ANNOTATIONS:
            pred_dir = exporting_request.pred_dir
            if not pred_dir:
                return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED, message="empty pred_dir")
            os.makedirs(pred_dir, exist_ok=True)

            gt_dir = exporting_request.gt_dir
            if not gt_dir:
                return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED, message="empty gt_dir")
            os.makedirs(pred_dir, exist_ok=True)

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_export, 1.0)]

    @classmethod
    def subtask_invoke_export(cls, request: backend_pb2.GeneralReq, user_labels: UserLabels, sandbox_root: str,
                              assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                              subtask_workdir: str, his_task_id: Optional[str],
                              in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        exporting_request = request.req_create_task.exporting
        media_location = assets_config['assetskvlocation']
        exporting_response = cls.exporting_cmd(repo_root=repo_root,
                                               label_storage_file=user_labels.storage_file,
                                               in_dataset_id=in_dataset_ids[0],
                                               annotation_format=utils.annotation_format_str(exporting_request.format),
                                               asset_dir=exporting_request.asset_dir,
                                               pred_dir=exporting_request.pred_dir,
                                               gt_dir=exporting_request.gt_dir,
                                               media_location=media_location,
                                               work_dir=subtask_workdir)

        return exporting_response

    @staticmethod
    def exporting_cmd(repo_root: str,
                      label_storage_file: str,
                      in_dataset_id: str,
                      annotation_format: str,
                      asset_dir: str,
                      pred_dir: Optional[str],
                      media_location: str,
                      work_dir: Optional[str] = None,
                      keywords: List[str] = None,
                      gt_dir: Optional[str] = None) -> backend_pb2.GeneralResp:
        exporting_cmd = [
            utils.mir_executable(), 'export', '--root', repo_root, '--media-location', media_location, '--asset-dir',
            asset_dir, '--src-revs', f"{in_dataset_id}@{in_dataset_id}", '--anno-format', annotation_format,
            '--user-label-file', label_storage_file,
        ]
        if keywords:
            exporting_cmd.append('--class_names')
            exporting_cmd.append(';'.join(keywords))
        if work_dir:
            exporting_cmd += ["-w", work_dir]
        if pred_dir:
            exporting_cmd += ["--pred-dir", pred_dir]
        if gt_dir:
            exporting_cmd += ["--gt-dir", gt_dir]

        return utils.run_command(exporting_cmd)
