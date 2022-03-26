import os
from typing import Dict

from mir.tools import mir_storage_ops, errors

from src.config import viz_settings
from src.libs import exceptions, app_logger


class MirStorageLoader:
    def __init__(self, sandbox_root: str, user_id: str, repo_id: str, branch_id: str, task_id: str):
        self.mir_root = os.path.join(sandbox_root, user_id, repo_id)
        self.branch_id = branch_id
        if not task_id:
            task_id = branch_id
        self.task_id = task_id

    def get_model_info(self) -> Dict:
        try:
            model_info = mir_storage_ops.MirStorageOps.load_single_model(
                mir_root=self.mir_root,
                mir_branch=self.branch_id,
                mir_task_id=self.task_id,
            )
        except errors.MirError:
            raise exceptions.ModelNotExists(f"model {self.branch_id} not found")

        return model_info

    def get_dataset_info(self) -> Dict:
        """
        exampled return data:
        {
            "class_ids_count": {3: 34},
            "ignored_labels": {'cat':5, },
            "negative_info": {
                "negative_images_cnt": 0,
                "project_negative_images_cnt": 0,
            },
            "total_images_cnt": 1,
        }
        """
        try:
            dataset_info = mir_storage_ops.MirStorageOps.load_single_dataset(
                mir_root=self.mir_root,
                mir_branch=self.branch_id,
                mir_task_id=self.task_id,
            )
        except ValueError as e:
            app_logger.logger.error(e)
            raise exceptions.BranchNotExists(f"dataset {self.branch_id} not exist from ymir command")

        return dataset_info

    def get_assets_content(self) -> Dict:
        """
        exampled data:
        {
            "all_asset_ids": ["asset_id"],
            "asset_ids_detail": {
                "asset_id": {
                    "metadata": {"asset_type": 2, "width": 1080, "height": 1620,},
                    "annotations": [{"box": {"x": 26, "y": 189, "w": 19, "h": 50}, "class_id": 2}],
                    "class_ids": [2, 3],
                }
            },
            "class_ids_index": {3: ["asset_id",],
        }
        """
        try:
            assets_info = mir_storage_ops.MirStorageOps.load_assets_content(
                mir_root=self.mir_root,
                mir_branch=self.branch_id,
                mir_task_id=self.task_id,
            )
        except ValueError as e:
            app_logger.logger.error(e)
            raise exceptions.BranchNotExists(f"branch {self.branch_id} not exist from ymir command")
        assets_info["class_ids_index"][viz_settings.VIZ_ALL_INDEX_CLASSIDS] = assets_info["all_asset_ids"]

        return assets_info
