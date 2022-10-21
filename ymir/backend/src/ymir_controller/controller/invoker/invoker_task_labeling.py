import logging
from typing import Dict, List, Optional, Tuple

from common_utils import labels
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.label_model import label_runner
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TaskLabelingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if len(request.in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid in_dataset_ids {request.in_dataset_ids}")
        try:
            utils.create_label_instance()
        except ValueError:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message="ill-configured label_tool")

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")

    @classmethod
    def register_subtasks(cls, request: backend_pb2.GeneralReq) -> List[Tuple[SubTaskType, float]]:
        return [(cls.subtask_invoke_label, 1.0)]

    @classmethod
    def subtask_invoke_label(cls, request: backend_pb2.GeneralReq, user_labels: labels.UserLabels, sandbox_root: str,
                             assets_config: Dict[str, str], repo_root: str, master_task_id: str, subtask_id: str,
                             subtask_workdir: str, his_task_id: Optional[str],
                             in_dataset_ids: List[str]) -> backend_pb2.GeneralResp:
        labeling_request = request.req_create_task.labeling
        logging.info(f"labeling_request: {labeling_request}")
        keywords = user_labels.main_name_for_ids(class_ids=list(request.in_class_ids))
        labeler_accounts = list(labeling_request.labeler_accounts)
        media_location = assets_config["assetskvlocation"]

        label_runner.start_label_task(
            repo_root=repo_root,
            working_dir=subtask_workdir,
            media_location=media_location,
            task_id=subtask_id,
            project_name=labeling_request.project_name,
            dataset_id=in_dataset_ids[0],
            keywords=keywords,
            collaborators=labeler_accounts,
            expert_instruction=labeling_request.expert_instruction_url,
            annotation_type=labeling_request.annotation_type,
        )

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")
