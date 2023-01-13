import json
import logging
import os
from pathlib import Path
import sys
from typing import Dict, Iterator

from requests.exceptions import ConnectionError, HTTPError, Timeout
import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.labels import ids_file_name
from common_utils.percent_log_util import LogState, PercentLogHandler
from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_import_dataset import TaskImportDatasetInvoker
from controller.utils import utils
from controller.utils.redis import rds
from controller.label_model.base import NotReadyError
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2


def trigger_mir_import(repo_root: str, task_id: str, index_file: str, des_annotation_path: str, media_location: str,
                       import_work_dir: str, object_type: int) -> None:
    TaskImportDatasetInvoker.importing_cmd(repo_root=repo_root,
                                           label_storage_file=os.path.join(os.path.dirname(repo_root), ids_file_name()),
                                           task_id=task_id,
                                           index_file=index_file,
                                           pred_dir='',
                                           gt_dir=des_annotation_path,
                                           media_location=media_location,
                                           work_dir=import_work_dir,
                                           unknown_types_strategy=backend_pb2.UnknownTypesStrategy.UTS_STOP,
                                           object_type=object_type)


def remove_json_file(des_annotation_path: str) -> None:
    if not os.path.isdir(des_annotation_path):
        logging.error(f"des_annotation_path not exist: {des_annotation_path}")
        return

    for annotation_file in os.listdir(des_annotation_path):
        if annotation_file.endswith(".json"):
            os.remove(os.path.join(des_annotation_path, annotation_file))


def iter_asset_dir(input_asset_dir: Path) -> Iterator[Path]:
    image_dirs = [i for i in input_asset_dir.iterdir() if i.is_dir()]
    for image_dir in image_dirs:
        for image_path in image_dir.iterdir():
            yield image_path


def generate_label_index_file(input_asset_dir: Path, annotation_dir: Path, object_type: int) -> Path:
    """
    filter assets paths against related annotation files
    """
    if object_type == mir_cmd_pb.ObjectType.OT_DET_BOX:
        labelled_assets_hashes = [i.stem for i in annotation_dir.iterdir() if i.suffix == ".xml"]
    else:
        with open(annotation_dir / "coco-annotations.json") as f:
            coco = json.load(f)
        labelled_assets_hashes = [Path(i["file_name"]).stem for i in coco["images"]]

    input_asset_paths = list(iter_asset_dir(input_asset_dir))
    output_file = input_asset_dir / "label_index.tsv"
    total_assets_count, labelled_assets_count = 0, 0
    with open(output_file, "w") as out_:
        for asset_path in input_asset_paths:
            total_assets_count += 1
            if asset_path.stem in labelled_assets_hashes:
                labelled_assets_count += 1
                out_.write(f"{asset_path}\n")
    logging.info(
        f"prepare annotation import: total assets {total_assets_count}, labelled assets {labelled_assets_count}"
    )
    return output_file


def update_label_task(label_instance: utils.LabelBase, task_id: str, project_info: Dict) -> None:
    percent = label_instance.get_task_completion_percent(project_info["project_id"])

    logging.info(f"label task <{task_id}> percent: {percent}")
    state = LogState.DONE if percent == 1 else LogState.RUNNING
    if state == LogState.DONE:
        # For remove some special tasks. Delete the task after labeling will save file
        object_type = int(project_info.get("object_type", mir_cmd_pb.ObjectType.OT_DET_BOX))
        des_annotation_path = project_info["des_annotation_path"]
        remove_json_file(des_annotation_path)
        try:
            label_instance.sync_export_storage(project_info["storage_id"])
            label_instance.fetch_label_result(project_info["project_id"],
                                              object_type,
                                              des_annotation_path)
        except NotReadyError:
            logging.info("label result not ready, try agiain later")
            return
        except (ConnectionError, HTTPError, Timeout) as e:
            sentry_sdk.capture_exception(e)
            logging.error(f"get label task {task_id} error: {e}, set task_id:{task_id} error")
            state = LogState.ERROR
        label_index_file = generate_label_index_file(
            Path(project_info["input_asset_dir"]), Path(des_annotation_path), object_type)
        trigger_mir_import(
            repo_root=project_info["repo_root"],
            task_id=task_id,
            index_file=str(label_index_file),
            des_annotation_path=des_annotation_path,
            media_location=project_info["media_location"],
            import_work_dir=project_info["import_work_dir"],
            object_type=object_type,
        )

        rds.hdel(label_task_config.MONITOR_MAPPING_KEY, task_id)
        logging.info(f"task {task_id} finished!!!")

    PercentLogHandler.write_percent_log(log_file=project_info["monitor_file_path"],
                                        tid=project_info["task_id"],
                                        percent=percent,
                                        state=state)


def lable_task_monitor() -> None:
    label_instance = utils.create_label_instance()
    project_mapping = rds.hgetall(label_task_config.MONITOR_MAPPING_KEY)
    for task_id, content in project_mapping.items():
        try:
            project_info = json.loads(content)
            update_label_task(label_instance, task_id, project_info)
        except FileNotFoundError:
            logging.exception("Monitor file not exists. Skip updating task %s with payload %s", task_id, content)
        except Exception:
            logging.exception("Unknown error. Skip updating task %s with payload %s", task_id, content)


if __name__ == "__main__":
    sentry_sdk.init(os.environ.get("LABEL_MONITOR_SENTRY_DSN", None))
    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s",
        datefmt="%Y%m%d-%H:%M:%S",
        level=logging.DEBUG,
    )
    scheduler = BlockingScheduler()
    scheduler.add_job(lable_task_monitor, "interval", seconds=label_task_config.LABEL_TASK_LOOP_SECONDS, jitter=120)
    logging.info("monitor_label_project is running...")
    scheduler.start()
