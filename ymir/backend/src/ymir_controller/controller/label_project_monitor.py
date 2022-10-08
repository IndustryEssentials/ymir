import json
import logging
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ElementTree

from requests.exceptions import ConnectionError, HTTPError, Timeout
import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import LogState, PercentLogHandler
from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_import_dataset import TaskImportDatasetInvoker
from controller.utils import utils
from controller.utils.redis import rds
from controller.label_model.base import NotReadyError
from proto import backend_pb2


def trigger_mir_import(repo_root: str, task_id: str, index_file: str, des_annotation_path: str, media_location: str,
                       import_work_dir: str) -> None:
    # trigger mir import
    TaskImportDatasetInvoker.importing_cmd(repo_root=repo_root,
                                           task_id=task_id,
                                           index_file=index_file,
                                           pred_dir='',
                                           gt_dir=des_annotation_path,
                                           media_location=media_location,
                                           work_dir=import_work_dir,
                                           unknown_types_strategy=backend_pb2.UnknownTypesStrategy.UTS_STOP)


def remove_json_file(des_annotation_path: str) -> None:
    if not os.path.isdir(des_annotation_path):
        logging.error(f"des_annotation_path not exist: {des_annotation_path}")
        return

    for annotation_file in os.listdir(des_annotation_path):
        if annotation_file.endswith(".json"):
            os.remove(os.path.join(des_annotation_path, annotation_file))


def _gen_index_file(des_annotation_dir: str, media_location: str) -> str:
    media_files = []
    des_annotation_path = Path(des_annotation_dir)
    media_path = Path(media_location)

    if label_task_config.LABEL_TOOL == label_task_config.LABEL_STUDIO:
        for annotation_file in des_annotation_path.iterdir():
            if annotation_file.suffix == ".json":
                with open(annotation_file) as f:
                    json_content = json.load(f)
                    pic_path = json_content["task"]["data"]["image"].replace("data/local-files/?d=", "")
                    media_files.append(pic_path)
    elif label_task_config.LABEL_TOOL == label_task_config.LABEL_FREE:
        for annotation_file in des_annotation_path.iterdir():
            if annotation_file.suffix == ".xml":
                annotation = ElementTree.parse(annotation_file)
                media_filename = annotation.findtext("filename")
                if media_filename:
                    media_filename = Path(media_filename).stem
                    # compatible with assets path pattern
                    media_files.append(str(media_path / media_filename[-2:] / media_filename))
    else:
        raise ValueError("LABEL_TOOL Error")

    index_file = des_annotation_path / "index.txt"
    with open(index_file, "w") as f:
        f.write("\n".join(media_files))

    return str(index_file)


def lable_task_monitor() -> None:
    label_instance = utils.create_label_instance()
    project_mapping = rds.hgetall(label_task_config.MONITOR_MAPPING_KEY)
    for task_id, content in project_mapping.items():
        project_info = json.loads(content)
        percent = label_instance.get_task_completion_percent(project_info["project_id"])

        logging.info(f"label task:{task_id} percent: {percent}")
        state = LogState.DONE if percent == 1 else LogState.RUNNING
        if state == LogState.DONE:
            # For remove some special tasks.Delete the task after labeling will save file
            remove_json_file(project_info["des_annotation_path"])
            try:
                label_instance.sync_export_storage(project_info["storage_id"])
                label_instance.convert_annotation_to_voc(project_info["project_id"],
                                                         project_info["des_annotation_path"])
            except NotReadyError:
                logging.info("label result not ready, try agiain later")
                continue
            except (ConnectionError, HTTPError, Timeout) as e:
                sentry_sdk.capture_exception(e)
                logging.error(f"get label task {task_id} error: {e}, set task_id:{task_id} error")
                state = LogState.ERROR
            index_file = _gen_index_file(project_info["des_annotation_path"], project_info["media_location"])
            trigger_mir_import(
                repo_root=project_info["repo_root"],
                task_id=task_id,
                index_file=index_file,
                des_annotation_path=project_info["des_annotation_path"],
                media_location=project_info["media_location"],
                import_work_dir=project_info["import_work_dir"],
            )

            rds.hdel(label_task_config.MONITOR_MAPPING_KEY, task_id)
            logging.info(f"task {task_id} finished!!!")

        PercentLogHandler.write_percent_log(log_file=project_info["monitor_file_path"],
                                            tid=project_info["task_id"],
                                            percent=percent,
                                            state=state)


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
