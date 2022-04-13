import logging
from typing import Dict, List

from common_utils import labels
from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.label_model import label_runner
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskLabelingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, sandbox_root: str, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def subtask_weights(cls) -> List[float]:
        return [1.0]

    @classmethod
    def subtask_invoke_0(cls, sandbox_root: str, repo_root: str, assets_config: Dict[str, str],
                         request: backend_pb2.GeneralReq, subtask_id: str, subtask_workdir: str,
                         previous_subtask_id: str, user_labels: labels.UserLabels) -> backend_pb2.GeneralResp:
        labeling_request = request.req_create_task.labeling
        logging.info(f"labeling_request: {labeling_request}")
        keywords = user_labels.get_main_names(class_ids=list(labeling_request.in_class_ids))
        labeler_accounts = list(labeling_request.labeler_accounts)
        media_location = assets_config["assetskvlocation"]

        label_runner.start_label_task(
            repo_root=repo_root,
            working_dir=subtask_workdir,
            media_location=media_location,
            task_id=subtask_id,
            project_name=labeling_request.project_name,
            dataset_id=labeling_request.dataset_id,
            keywords=keywords,
            collaborators=labeler_accounts,
            expert_instruction=labeling_request.expert_instruction_url,
            export_annotation=labeling_request.export_annotation,
        )

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")
