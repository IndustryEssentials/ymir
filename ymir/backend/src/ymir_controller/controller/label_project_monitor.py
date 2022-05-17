import json
import logging
import os
import sys

from requests.exceptions import ConnectionError, HTTPError, Timeout
import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from common_utils.percent_log_util import LogState, PercentLogHandler
from controller.config import label_task as label_task_config
from controller.invoker.invoker_task_importing import TaskImportingInvoker
from controller.utils import utils
from controller.utils.redis import rds


def trigger_mir_import(
    repo_root: str, task_id: str, index_file: str, des_annotation_path: str, media_location: str, import_work_dir: str
) -> None:
    # trigger mir import
    TaskImportingInvoker.importing_cmd(
        repo_root, task_id, index_file, des_annotation_path, media_location, import_work_dir, name_strategy_ignore=False
    )


def remove_json_file(des_annotation_path: str) -> None:
    if not os.path.isdir(des_annotation_path):
        logging.error(f"des_annotation_path not exist: {des_annotation_path}")
        return

    for one_file in os.listdir(des_annotation_path):
        if one_file.endswith(".json"):
            os.remove(os.path.join(des_annotation_path, one_file))


def _gen_index_file(des_annotation_path: str) -> str:
    media_files = []

    if label_task_config.LABEL_STUDIO == label_task_config.LABEL_TOOL:
        for one_file in os.listdir(des_annotation_path):
            if one_file.endswith(".json"):
                with open(os.path.join(des_annotation_path, one_file)) as f:
                    json_content = json.load(f)
                    pic_path = json_content["task"]["data"]["image"].replace("data/local-files/?d=", "")
                    media_files.append(pic_path)
    elif label_task_config.LABEL_FREE == label_task_config.LABEL_TOOL:
        des_annotation_media_path = os.path.join(des_annotation_path, "images")
        if os.path.isdir(des_annotation_media_path):
            for one_file in os.listdir(des_annotation_media_path):
                if os.path.splitext(one_file)[1].lower() in [".jpeg", ".jpg", ".png"]:
                    media_files.append(os.path.join(des_annotation_media_path, one_file))
    else:
        raise ValueError("LABEL_TOOL Error")

    index_file = os.path.join(des_annotation_path, "index.txt")
    with open(index_file, "w") as f:
        f.write("\n".join(media_files))

    return index_file


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
                label_instance.convert_annotation_to_voc(
                    project_info["project_id"], project_info["des_annotation_path"]
                )
            except (ConnectionError, HTTPError, Timeout) as e:
                sentry_sdk.capture_exception(e)
                logging.error(f"get label task {task_id} error: {e}, set task_id:{task_id} error")
                state = LogState.ERROR
            index_file = _gen_index_file(project_info["des_annotation_path"])
            trigger_mir_import(
                project_info["repo_root"],
                task_id,
                index_file,
                project_info["des_annotation_path"],
                project_info["media_location"],
                project_info["import_work_dir"],
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
