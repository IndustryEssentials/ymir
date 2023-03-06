import logging
from typing import Dict, List, Optional, Tuple

from common_utils import labels
from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_base import SubTaskType, TaskBaseInvoker
from controller.label_model import label_runner
from controller.utils import utils
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2
from mir.protos import mir_command_pb2 as mir_cmd_pb


class TaskLabelingInvoker(TaskBaseInvoker):
    def task_pre_invoke(self, request: backend_pb2.GeneralReq) -> backend_pb2.GeneralResp:
        if len(request.in_dataset_ids) != 1:
            return utils.make_general_response(code=CTLResponseCode.ARG_VALIDATION_FAILED,
                                               message=f"Invalid in_dataset_ids {request.in_dataset_ids}")

        if (
            label_task_config.LABEL_TOOL == label_task_config.LABEL_STUDIO
            and request.req_create_task.labeling.object_type == mir_cmd_pb.ObjectType.OT_SEG
        ):
            return utils.make_general_response(code=CTLResponseCode.INVOKER_LABEL_TASK_SEG_NOT_SUPPORTED,
                                               message="label_studio does not support segmentation")
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
    def need_index_repo(cls) -> bool:
        return False

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
            label_storage_file=user_labels.storage_file,
            working_dir=subtask_workdir,
            media_location=media_location,
            task_id=subtask_id,
            project_name=labeling_request.project_name,
            dataset_id=in_dataset_ids[0],
            keywords=keywords,
            collaborators=labeler_accounts,
            expert_instruction=labeling_request.expert_instruction_url,
            annotation_type=labeling_request.annotation_type,
            object_type=labeling_request.object_type,
            is_instance_segmentation=labeling_request.is_instance_segmentation,
        )

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")
