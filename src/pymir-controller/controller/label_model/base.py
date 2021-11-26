import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List

from controller import config
from controller.utils.redis import rds


def catch_label_task_error(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args: tuple, **kwargs: Any) -> object:
        try:
            _ret = f(*args, **kwargs)
        except Exception as e:
            status = f'{kwargs["task_id"]} {int(datetime.now().timestamp())} 0 {config.TASK_ERROR}'
            LabelBase.write_project_status(kwargs["monitor_file_path"], f"{status}\n{e}")
            _ret = None
        return _ret

    return wrapper


class LabelBase(ABC):
    @abstractmethod
    def create_label_project(self, project_name: str, keywords: List, collaborators: List, expert_instruction: str,
                             **kwargs: Dict) -> int:
        # Create a label project, add extra args in kwargs if you need
        pass

    @abstractmethod
    def set_import_storage(self, project_id: int, import_path: str) -> int:
        # Create import storage to label tool
        pass

    @abstractmethod
    def set_export_storage(self, project_id: int, export_path: str) -> None:
        # Create export storage to label tool
        pass

    @abstractmethod
    def sync_import_storage(self, storage_id: int) -> Any:
        # Sync tasks from import storage to label tool
        pass

    @abstractmethod
    def convert_annotation_to_voc(self, project_id: int, des_path: str) -> Any:
        # because ymir supporting voc files to import
        pass

    @abstractmethod
    def get_task_completion_percent(self, project_id: int) -> float:
        pass

    @abstractmethod
    def run(self, **kwargs: Dict) -> Any:
        # start a label task
        pass

    @staticmethod
    def write_project_status(project_status_path: str, content: str) -> None:
        """
        worker need to log self status to project_status_path, controller will scan the file to get status
        first line:
        task_id, timestamp, percent, state, *_ = first_line[0].split()
        state in ["pending", "running", "done", "error"]
        """
        with open(project_status_path, "w") as f:
            f.write(content)

    # now we have to loop label task for get status
    # maybe add API for labeling tool to report self status later https://labelstud.io/guide/webhooks.html
    @staticmethod
    def store_label_task_mapping(
        project_id: int,
        task_id: str,
        monitor_file_path: str,
        des_annotation_path: str,
        repo_root: str,
        media_location: str,
        import_work_dir: str
    ) -> None:
        # store into redis for loop get status
        label_task_content = dict(
            project_id=project_id,
            task_id=task_id,
            monitor_file_path=monitor_file_path,
            des_annotation_path=des_annotation_path,
            repo_root=repo_root,
            media_location=media_location,
            import_work_dir=import_work_dir
        )

        rds.hmset(config.MONITOR_MAPPING_KEY, {task_id: json.dumps(label_task_content)})
