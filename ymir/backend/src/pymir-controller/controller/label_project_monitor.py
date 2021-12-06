import json
import logging
import os
import sys
from datetime import datetime

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controller.invoker.invoker_task_importing import TaskImportingInvoker
from controller import config
from controller.label_model.label_studio import LabelStudio
from controller.utils.redis import rds
from controller.utils.app_logger import logger


def trigger_mir_import(
    repo_root: str, task_id: str, index_file: str, des_annotation_path: str, media_location: str, import_work_dir: str
) -> None:
    # trigger mir import
    TaskImportingInvoker.importing_cmd(
        repo_root, task_id, index_file, des_annotation_path, media_location, import_work_dir, name_strategy_ignore=False
    )


def _gen_index_file(des_annotation_path: str) -> str:
    media_files = []
    for one_file in os.listdir(des_annotation_path):
        if one_file.endswith(".json"):
            with open(os.path.join(des_annotation_path, one_file)) as f:
                json_content = json.load(f)
                pic_path = json_content["task"]["data"]["image"].replace("data/local-files/?d=", "")
                media_files.append(pic_path)

    index_file = os.path.join(des_annotation_path, "index.txt")
    with open(index_file, "w") as f:
        f.write("\n".join(media_files))

    return index_file


def lable_task_monitor() -> None:
    if config.LABEL_STUDIO == config.LABEL_TOOL:
        label_instance = LabelStudio()
    else:
        raise ValueError("Error! Please setting your label tools")

    project_mapping = rds.hgetall(config.MONITOR_MAPPING_KEY)
    for task_id, content in project_mapping.items():
        project_info = json.loads(content)
        percent = label_instance.get_task_completion_percent(project_info['project_id'])

        logger.info(f'label task:{task_id} percent: {percent}')
        state = config.TASK_DONE if percent == 1 else config.TASK_RUNNING
        if state == config.TASK_DONE:
            try:
                label_instance.convert_annotation_to_voc(project_info['project_id'], project_info["des_annotation_path"])
            except requests.HTTPError as e:
                # TODO:(chao) add sentry
                logger.error(f'get label task {task_id} voc error: {e}, set task_id:{task_id} error')
                state = config.TASK_ERROR
            index_file = _gen_index_file(project_info["des_annotation_path"])
            trigger_mir_import(
                project_info["repo_root"],
                task_id,
                index_file,
                project_info["des_annotation_path"],
                project_info["media_location"],
                project_info["import_work_dir"],
            )

            rds.hdel(config.MONITOR_MAPPING_KEY, task_id)
            logging.info(f'task {task_id} finished!!!')

        content = f'{project_info["task_id"]}\t{int(datetime.now().timestamp())}\t{percent}\t{state}'
        label_instance.write_project_status(project_info["monitor_file_path"], content)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(lable_task_monitor, "interval", seconds=config.LABEL_TASK_LOOP_SECONDS, jitter=120)
    logger.info("monitor_label_project is running...")
    scheduler.start()
