from typing import Dict

from src import config
from src.libs import utils
from src.viz_models import pb_reader
from src.viz_models.base import BaseModel


class Task(BaseModel):
    def format_model_info(self, model_info: Dict) -> Dict:
        result = dict(
            model_id=model_info["model_hash"],
            model_mAP=model_info["mean_average_precision"],
            task_parameters=model_info["task_parameters"],
            executor_config=model_info["executor_config"],
        )

        return result

    @utils.time_it
    def get_model_info(self) -> Dict:
        # not need cache, it stored in app
        raw_model_message = pb_reader.MirStorageLoader(
            config.SANDBOX_ROOT, self.user_id, self.repo_id, self.branch_id
        ).get_model_info()

        return self.format_model_info(raw_model_message)
