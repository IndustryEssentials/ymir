from typing import Dict

from controller.invoker.invoker_task_base import TaskBaseInvoker
from controller.label_model import label_runner
from controller.utils import utils
from controller.utils.labels import LabelFileHandler
from id_definition.error_codes import CTLResponseCode
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
            repo_root=repo_root,
            working_dir=working_dir,
            media_location=media_location,
            task_id=task_id,
            project_name=labeling_request.project_name,
            dataset_id=labeling_request.dataset_id,
            keywords=keywords,
            collaborators=labeler_accounts,
            expert_instruction=labeling_request.expert_instruction_url,
            export_annotation=labeling_request.export_annotation,
        )

        return utils.make_general_response(CTLResponseCode.CTR_OK, "")
