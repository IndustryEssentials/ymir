import os
from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker, write_done_progress
from controller.utils import code, utils
from proto import backend_pb2


class TaskExportingInvoker(TaskBaseInvoker):
    @classmethod
    @write_done_progress
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict, working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        exporting_request = request.req_create_task.exporting
        print('exporting_requests: {}'.format(exporting_request))

        asset_dir = exporting_request.asset_dir
        if not asset_dir:
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "empty asset_dir")
        os.makedirs(asset_dir, exist_ok=True)

        annotation_dir = exporting_request.annotation_dir
        if exporting_request.format != backend_pb2.LabelFormat.NO_ANNOTATION:
            if not annotation_dir:
                return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "empty anno_dir")
            os.makedirs(annotation_dir, exist_ok=True)

        media_location = assets_config['assetskvlocation']
        exporting_response = cls.exporting_cmd(repo_root=repo_root,
                                               dataset_id=exporting_request.dataset_id,
                                               format=utils.annotation_format_str(exporting_request.format),
                                               asset_dir=asset_dir,
                                               annotation_dir=annotation_dir,
                                               media_location=media_location,
                                               work_dir=working_dir)

        return exporting_response

    @staticmethod
    def exporting_cmd(repo_root: str, dataset_id: str, format: str, asset_dir: str, annotation_dir: str,
                      media_location: str, work_dir: str) -> backend_pb2.GeneralResp:
        exporting_cmd = (
            f"cd {repo_root} && mir export --media-location {media_location} --asset-dir {asset_dir} "
            f"--annotation-dir {annotation_dir} --src-revs {dataset_id} --format {format} -w {work_dir}"
        )

        return utils.run_command(exporting_cmd)

    def _repr(self) -> str:
        exporting_request = self._request.req_create_task.exporting
        return (
            "task_exporting: user: {}, repo: {} task_id: {} src-revs: {} asset-dir: {} annotation-dir: {} format: {}".
            format(self._request.user_id, self._request.repo_id, self._task_id, exporting_request.dataset_id,
                   exporting_request.asset_dir, exporting_request.annotation_dir, exporting_request.format))
