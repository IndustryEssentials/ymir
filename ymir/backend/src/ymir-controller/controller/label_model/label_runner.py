import os
from typing import Tuple, List

from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.label_model.aios import AIOS
from controller.label_model.label_studio import LabelStudio
from controller.label_model.request_handler import RequestHandler
from controller.utils import utils
from controller.utils.app_logger import logger
from proto import backend_pb2


def prepare_label_dir(working_dir: str, task_id: str) -> Tuple[str, str, str, str, str]:
    task_data_dir = f"{working_dir}/label_{task_id}"
    input_asset_dir = os.path.join(task_data_dir, "Images")
    os.makedirs(input_asset_dir, exist_ok=True)

    export_path = os.path.join(task_data_dir, "label_studio_output")
    os.makedirs(export_path, exist_ok=True)

    # keep same name as other task
    monitor_file_path = os.path.join(working_dir, "out", "monitor.txt")

    export_work_dir = os.path.join(working_dir, "export_work_dir")
    os.makedirs(export_work_dir, exist_ok=True)
    import_work_dir = os.path.join(working_dir, "import_work_dir")
    os.makedirs(import_work_dir, exist_ok=True)

    return input_asset_dir, export_path, monitor_file_path, export_work_dir, import_work_dir


def trigger_ymir_export(repo_root: str, dataset_id: str, input_asset_dir: str, media_location: str,
                        export_work_dir: str, keywords: List[str]) -> None:
    # trigger ymir export, so that we can get pictures from ymir
    format_str = utils.annotation_format_str(backend_pb2.LabelFormat.LABEL_STUDIO_JSON)

    TaskExportingInvoker.exporting_cmd(repo_root=repo_root,
                                       dataset_id=dataset_id,
                                       annotation_format=format_str,
                                       asset_dir=input_asset_dir,
                                       annotation_dir=input_asset_dir,
                                       media_location=media_location,
                                       work_dir=export_work_dir,
                                       keywords=keywords)


def start_label_task(
    repo_root: str,
    working_dir: str,
    media_location: str,
    task_id: str,
    project_name: str,
    dataset_id: str,
    keywords: List,
    collaborators: List,
    expert_instruction: str,
    export_annotation: bool,
) -> None:
    logger.info("start label task!!!")
    # set your lable tools name
    request_handler = RequestHandler(
        url=label_task_config.LABEL_TOOL_URL, headers={"Authorization": label_task_config.LABEL_TOOL_TOKEN}
    )
    if label_task_config.LABEL_TOOL == label_task_config.LABEL_STUDIO:
        label_instance = LabelStudio(request_handler)
    elif label_task_config.LABEL_TOOL == label_task_config.AIOS:
        label_instance = AIOS(request_handler)  # type: ignore
    else:
        raise ValueError("Error! Please setting your label tools")

    input_asset_dir, export_path, monitor_file_path, export_work_dir, import_work_dir = prepare_label_dir(
        working_dir, task_id)
    trigger_ymir_export(repo_root=repo_root,
                        dataset_id=dataset_id,
                        input_asset_dir=input_asset_dir,
                        media_location=media_location,
                        export_work_dir=export_work_dir,
                        keywords=keywords)
    label_instance.run(task_id=task_id,
                       project_name=project_name,
                       keywords=keywords,
                       collaborators=collaborators,
                       expert_instruction=expert_instruction,
                       input_asset_dir=input_asset_dir,
                       export_path=export_path,
                       monitor_file_path=monitor_file_path,
                       repo_root=repo_root,
                       media_location=media_location,
                       import_work_dir=import_work_dir,
                       use_pre_annotation=export_annotation)
    logger.info("finish label task!!!")
