import json
import logging
import os
from pathlib import Path
from typing import Tuple, List, Optional

from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_exporting import TaskExportingInvoker
from controller.utils import utils
from mir.protos import mir_command_pb2 as mir_cmd_pb


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


def get_mir_export_fmt(label_tool: str, object_type: int) -> str:
    """
    ad hoc
    labelfree uses coco for segmentation dataset, LS for detection dataset
    """
    if label_tool == label_task_config.LABEL_FREE and object_type == mir_cmd_pb.ObjectType.OT_SEG:
        return utils.annotation_format_str(mir_cmd_pb.ExportFormat.EF_COCO_JSON)
    return utils.annotation_format_str(mir_cmd_pb.ExportFormat.EF_LS_JSON)


def fix_exported_coco_annotation_image_path(dirname: str) -> None:
    """
    fix image filename in mir exported coco-annotations.json
    """
    coco_path = Path(dirname) / label_task_config.MIR_COCO_ANNOTATION_FILENAME
    if not coco_path.is_file:
        return
    with open(coco_path) as f:
        coco = json.load(f)
    for image in coco["images"]:
        image["file_name"] = str(Path(Path(image["file_name"]).stem[-2:], image["file_name"]))
    with open(coco_path, "w") as f:
        json.dump(coco, f)


def trigger_ymir_export(repo_root: str, label_storage_file: str, dataset_id: str, input_asset_dir: str,
                        media_location: str, export_work_dir: str, keywords: List[str],
                        annotation_type: Optional[int], object_type: int) -> None:
    # trigger ymir export, so that we can get pictures from ymir
    format_str = get_mir_export_fmt(label_task_config.LABEL_TOOL, object_type)

    gt_dir: Optional[str] = None
    pred_dir: Optional[str] = None
    if annotation_type == mir_cmd_pb.AnnotationType.AT_GT:
        gt_dir = input_asset_dir
    elif annotation_type == mir_cmd_pb.AnnotationType.AT_PRED:
        pred_dir = input_asset_dir

    TaskExportingInvoker.exporting_cmd(repo_root=repo_root,
                                       label_storage_file=label_storage_file,
                                       in_dataset_id=dataset_id,
                                       annotation_format=format_str,
                                       asset_dir=input_asset_dir,
                                       pred_dir=pred_dir,
                                       gt_dir=gt_dir,
                                       media_location=media_location,
                                       work_dir=export_work_dir,
                                       keywords=keywords)
    annotation_dir = gt_dir or pred_dir
    if (
        annotation_dir is not None
        and format_str == utils.annotation_format_str(mir_cmd_pb.ExportFormat.EF_COCO_JSON)
    ):
        fix_exported_coco_annotation_image_path(annotation_dir)


def start_label_task(
    repo_root: str,
    label_storage_file: str,
    working_dir: str,
    media_location: str,
    task_id: str,
    project_name: str,
    dataset_id: str,
    keywords: List,
    collaborators: List,
    expert_instruction: str,
    annotation_type: Optional[int],
    object_type: int,
    is_instance_segmentation: bool,
) -> None:
    logging.info("start label task!!!")
    label_instance = utils.create_label_instance()
    input_asset_dir, export_path, monitor_file_path, export_work_dir, import_work_dir = prepare_label_dir(
        working_dir, task_id)
    trigger_ymir_export(repo_root=repo_root,
                        label_storage_file=label_storage_file,
                        dataset_id=dataset_id,
                        input_asset_dir=input_asset_dir,
                        media_location=media_location,
                        export_work_dir=export_work_dir,
                        keywords=keywords,
                        annotation_type=annotation_type,
                        object_type=object_type)
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
                       use_pre_annotation=bool(annotation_type),
                       object_type=object_type,
                       is_instance_segmentation=is_instance_segmentation)
    logging.info("finish label task!!!")
