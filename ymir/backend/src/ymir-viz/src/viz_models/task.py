from typing import Dict

from src import config
from src.libs import utils
from src.viz_models import pb_reader
from src.viz_models.base import BaseModel


class Task(BaseModel):
    def format_model_info(self, raw_model_message: Dict) -> Dict:
        model_info = raw_model_message["tasks"][self.branch_id]
        result = dict(
            model_id=model_info["model"]["model_hash"],
            model_mAP=model_info["model"]["mean_average_precision"],
            task_type=model_info["type"],
        )

        return result

    @utils.time_it
    def get_model_info(self) -> Dict:
        # not need cache, it stored in app
        raw_model_message = pb_reader.MirStorageLoader(
            config.SANDBOX_ROOT, self.user_id, self.repo_id, self.branch_id
        ).get_tasks_content()

        return self.format_model_info(raw_model_message)
