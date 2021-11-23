import os

from controller.invoker.invoker_task_base import TaskBaseInvoker, write_done_progress
from controller.utils import code, utils
from proto import backend_pb2


class TaskCopyInvoker(TaskBaseInvoker):
    @classmethod
    @write_done_progress
    def task_invoke(cls, sandbox_root: str, repo_root: str, assets_config: str, working_dir: str,
                    task_monitor_file: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        copy_request = request.req_create_task.copy

        if not (copy_request.src_user_id and copy_request.src_repo_id):
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ, "Invalid src user and/or repo id")

        src_root = os.path.join(sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        if not os.path.isdir(src_root):
            return utils.make_general_response(code.ResCode.CTR_INVALID_SERVICE_REQ,
                                               "Invalid src root: {}".format(src_root))

        sub_task_id_0 = utils.sub_task_id(request.task_id, 0)
        copy_response = cls.copying_cmd(repo_root=repo_root,
                                        task_id=sub_task_id_0,
                                        src_root=src_root,
                                        src_dataset_id=copy_request.src_dataset_id,
                                        work_dir=working_dir)

        return copy_response

    @staticmethod
    def copying_cmd(repo_root: str, task_id: str, src_root: str, src_dataset_id: str,
                    work_dir: str) -> backend_pb2.GeneralResp:
        copying_cmd_str = (
            f"cd {repo_root} && mir copy --src-root {src_root} --dst-rev {task_id}@{task_id} "
            f"--src-revs {src_dataset_id}@{src_dataset_id} -w {work_dir}"
        )

        return utils.run_command(copying_cmd_str)

    def _repr(self) -> str:
        return ("task_copy: user: {}, repo: {} task_id: {} copy_ruquest: {}".format(self._request.user_id,
                                                                                    self._request.repo_id,
                                                                                    self._task_id,
                                                                                    self._request.req_create_task.copy))
