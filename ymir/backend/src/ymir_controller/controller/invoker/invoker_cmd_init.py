import os
import pathlib

from common_utils import labels
from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, revs
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class InitInvoker(BaseMirControllerInvoker):
    def _need_work_dir(self) -> bool:
        return False

    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_invoker(
            invoker=self,
            prerequisites=[
                checker.Prerequisites.CHECK_USER_ID,
                checker.Prerequisites.CHECK_REPO_ID,
                checker.Prerequisites.CHECK_REPO_ROOT_NOT_EXIST,
            ],
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        repo_path = pathlib.Path(self._repo_root)
        repo_path.mkdir(parents=True, exist_ok=True)

        link_dst_dir = os.path.join(self._repo_root, '.mir')
        os.makedirs(link_dst_dir, exist_ok=True)
        link_dst_file = os.path.join(link_dst_dir, labels.ids_file_name())
        os.symlink(self._label_storage_file, link_dst_file)

        command = [utils.mir_executable(), 'init', '--root', self._repo_root]
        command.extend(
            ['--with-empty-rev',
             revs.join_tvt_branch_tid(branch_id=self._request.task_id, tid=self._request.task_id)])

        return utils.run_command(
            cmd=command,
            error_code=CTLResponseCode.INVOKER_INIT_ERROR,
        )
