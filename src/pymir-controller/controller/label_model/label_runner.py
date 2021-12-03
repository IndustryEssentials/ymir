import os
from typing import Tuple, List

from controller import config
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.label_model.label_studio import LabelStudio
from controller.utils.app_logger import logger


def prepare_label_dir(working_dir: str, task_id: str) -> Tuple[str, str, str, str, str]:
    asset_dir = os.path.join(working_dir, f"label_{task_id}", "Images")
    os.makedirs(asset_dir, exist_ok=True)

    export_path = os.path.join(working_dir, "label_{task_id}".format(task_id=task_id), "label_studio_output")
    os.makedirs(export_path, exist_ok=True)

    # keep same name as other task
    monitor_file_path = os.path.join(working_dir, "out", "monitor.txt")

    export_work_dir = os.path.join(working_dir, "export_work_dir")
    os.makedirs(export_work_dir, exist_ok=True)
    import_work_dir = os.path.join(working_dir, "import_work_dir")
    os.makedirs(import_work_dir, exist_ok=True)

    return asset_dir, export_path, monitor_file_path, export_work_dir, import_work_dir


def trigger_ymir_export(repo_root: str, dataset_id: str, asset_dir: str, media_location: str, export_work_dir: str) -> None:
    # trigger ymir export, so that we can get pictures from ymir
    TaskExportingInvoker.exporting_cmd(
        repo_root=repo_root,
        dataset_id=dataset_id,
        format="none",
        asset_dir=asset_dir,
        annotation_dir=asset_dir,
        media_location=media_location,
        work_dir=export_work_dir
    )


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
) -> None:
    logger.info("start label task!!!")
    # set your lable tools name
    if config.LABEL_STUDIO == config.LABEL_TOOL:
        label_instance = LabelStudio()
    else:
        raise ValueError("Error! Please setting your label tools")

    asset_dir, export_path, monitor_file_path, export_work_dir, import_work_dir = prepare_label_dir(
        working_dir, task_id
    )
    trigger_ymir_export(repo_root, dataset_id, asset_dir, media_location, export_work_dir)
    label_instance.run(
        task_id=task_id,
        project_name=project_name,
        keywords=keywords,
        collaborators=collaborators,
        expert_instruction=expert_instruction,
        asset_dir=asset_dir,
        export_path=export_path,
        monitor_file_path=monitor_file_path,
        repo_root=repo_root,
        media_location=media_location,
        import_work_dir=import_work_dir
    )
    logger.info("finish label task!!!")
