from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.utils import code, utils
from ymir.protos import mir_controller_service_pb2 as mirsvrpb

from ymir.ids import class_ids
from controller.label_model import label_runner


class TaskLabelingInvoker(TaskBaseInvoker):
    @classmethod
    def task_invoke(
        cls,
        sandbox_root: str,
        repo_root: str,
        assets_config: Dict[str, str],
        working_dir: str,
        task_monitor_file: str,
        request: mirsvrpb.GeneralReq,
    ) -> mirsvrpb.GeneralResp:
        labeling_request = request.req_create_task.labeling
        class_ids_ins = class_ids.ClassIdManager()
        keywords = [class_ids_ins.main_name_for_id(clas_id) for clas_id in labeling_request.in_class_ids]
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
