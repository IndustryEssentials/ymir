from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.label_model import label_runner
from controller.utils import code, utils
from controller.utils.labels import LabelFileHandler
from proto import backend_pb2


class TaskLabelingInvoker(TaskBaseInvoker):
    @classmethod
    def task_invoke(
        cls,
        sandbox_root: str,
        repo_root: str,
        assets_config: Dict[str, str],
        working_dir: str,
        task_monitor_file: str,
        request: backend_pb2.GeneralReq,
    ) -> backend_pb2.GeneralResp:
        labeling_request = request.req_create_task.labeling
        label_handler = LabelFileHandler(repo_root)
        keywords = label_handler.get_main_labels_by_ids(labeling_request.in_class_ids)
        labeler_accounts = list(labeling_request.labeler_accounts)
        media_location = assets_config["assetskvlocation"]
        task_id = request.task_id

        label_runner.start_label_task(
            repo_root,
            working_dir,
            media_location,
            task_id,
            labeling_request.project_name,
            labeling_request.dataset_id,
            keywords,
            labeler_accounts,
            labeling_request.expert_instruction_url,
        )

        return utils.make_general_response(code.ResCode.CTR_OK, "")

    def _repr(self) -> str:
        labeling_request = self._request.req_create_task.labeling
        return "task_labeling: user: {}, repo: {} task_id: {} labeling_request: {}".format(
            self._request.user_id, self._request.repo_id, self._task_id, labeling_request)
