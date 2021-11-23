import logging
import os
from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker, write_done_progress
from controller.utils import code, utils
from proto import backend_pb2


class TaskImportingInvoker(TaskBaseInvoker):
    @classmethod
    @write_done_progress
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str], working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        importing_request = request.req_create_task.importing

        # Prepare media index-file
        media_dir, anno_dir = importing_request.asset_dir, importing_request.annotation_dir
        if not (os.access(media_dir, os.R_OK) and os.access(anno_dir, os.R_OK)):
            error_str = "invalid permissions: \n{}\n{}".format(media_dir, anno_dir)
            logging.error(error_str)
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, error_str)

        media_files = [os.path.join(media_dir, f) for f in os.listdir(media_dir) if f.endswith('.jpg')]
        index_file = os.path.join(working_dir, 'index.txt')
        with open(index_file, 'w') as f:
            f.write('\n'.join(media_files))

        sub_task_id_0 = utils.sub_task_id(request.task_id, 0)
        media_location = assets_config['assetskvlocation']
        importing_response = cls.importing_cmd(repo_root=repo_root,
                                               task_id=sub_task_id_0,
                                               index_file=index_file,
                                               annotation_dir=anno_dir,
                                               media_location=media_location,
                                               work_dir=working_dir)

        return importing_response

    @staticmethod
    def importing_cmd(repo_root: str, task_id: str, index_file: str, annotation_dir: str,
                      media_location: str, work_dir: str) -> backend_pb2.GeneralResp:
        importing_cmd = (
            f"cd {repo_root} && mir import --dataset-name {task_id} --dst-rev {task_id}@{task_id} "
            f"--src-revs master --index-file {index_file} --annotation-dir {annotation_dir} "
            f"--gen-dir {media_location} -w {work_dir}"
        )

        return utils.run_command(importing_cmd)

    def _repr(self) -> str:
        importing_request = self._request.req_create_task.importing
        return ("task_importing: user: {}, repo: {} task_id: {} asset-dir: {} annotation-dir: {}".format(
            self._request.user_id, self._request.repo_id, self._task_id, importing_request.asset_dir,
            importing_request.annotation_dir))
