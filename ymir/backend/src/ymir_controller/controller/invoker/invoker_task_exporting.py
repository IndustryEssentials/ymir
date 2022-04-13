import logging
import os
from typing import Dict, List
from common_utils.labels import UserLabels

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskExportingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        exporting_request = request.req_create_task.exporting
        logging.info(f"exporting_requests: {exporting_request}")
        asset_dir = exporting_request.asset_dir
        if not asset_dir:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED, message="empty asset_dir")
        os.makedirs(asset_dir, exist_ok=True)

        annotation_dir = exporting_request.annotation_dir
        if exporting_request.format != backend_pb2.LabelFormat.NO_ANNOTATION:
            if not annotation_dir:
                return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                                   message="empty annotation_dir")
            os.makedirs(annotation_dir, exist_ok=True)

        return utils.make_general_response(code=CTLResponseCode.CTR_OK, message="")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: UserLabels) -> backend_pb2.GeneralResp:
        exporting_request = request.req_create_task.exporting
        asset_dir = exporting_request.asset_dir
        annotation_dir = exporting_request.annotation_dir
        media_location = assets_config['assetskvlocation']
        exporting_response = cls.exporting_cmd(repo_root=repo_root,
                                               dataset_id=exporting_request.dataset_id,
                                               annotation_format=utils.annotation_format_str(exporting_request.format),
                                               asset_dir=asset_dir,
                                               annotation_dir=annotation_dir,
                                               media_location=media_location,
                                               work_dir=subtask_workdir)

        return exporting_response

    @staticmethod
    def exporting_cmd(repo_root: str,
                      dataset_id: str,
                      annotation_format: str,
                      asset_dir: str,
                      annotation_dir: str,
                      media_location: str,
                      work_dir: str,
                      keywords: List[str] = None) -> backend_pb2.GeneralResp:
        exporting_cmd = [
            utils.mir_executable(), 'export', '--root', repo_root, '--media-location', media_location, '--asset-dir',
            asset_dir, '--annotation-dir', annotation_dir, '--src-revs', f"{dataset_id}@{dataset_id}", '--format',
            annotation_format, '-w', work_dir
        ]
        if keywords:
            exporting_cmd.append('--cis')
            exporting_cmd.append(';'.join(keywords))

        return utils.run_command(exporting_cmd)
