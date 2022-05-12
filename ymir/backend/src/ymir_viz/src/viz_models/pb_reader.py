import logging
import os
from typing import Dict

from mir.tools import mir_storage_ops, errors

from src.config import viz_settings
from src.libs import exceptions


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
        return value example:
        {
            "class_ids_count": {3: 34},
            "class_names_count": {'cat': 34},
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
            logging.error(e)
            raise exceptions.BranchNotExists(f"dataset {self.branch_id} not exist from ymir command")

        return dataset_info

    def get_assets_content(self) -> Dict:
        """
        return value example:
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
            logging.error(e)
            raise exceptions.BranchNotExists(f"branch {self.branch_id} not exist from ymir command")
        assets_info["class_ids_index"][viz_settings.VIZ_ALL_INDEX_CLASSIDS] = assets_info["all_asset_ids"]

        return assets_info

    def get_dataset_evaluations(self) -> Dict:
        """
        return value example:
        {
           "dataset_hash":{
              "iou_averaged_evaluation":{
                 "ci_averaged_evaluation":{
                    "ap":1.0,
                    "ar":1.0,
                    "fn":0,
                    "fp":0,
                    "tp":4329
                 },
                 "ci_evaluations":{
                    "4":{
                       "ap":1.0,
                       "ar":1.0,
                       "fn":0,
                       "fp":0,
                       "tp":91
                    }
                 },
                 "topic_evaluations":{}
              },
              "iou_evaluations":{
                 "0.50":{
                    "ci_averaged_evaluation":{
                       "ap":1.0,
                       "ar":1.0,
                       "fn":0,
                       "fp":0,
                       "tp":4329
                    },
                    "ci_evaluations":{
                       "2":{
                          "ap":1.0,
                          "ar":1.0,
                          "fn":0,
                          "fp":0,
                          "tp":4238
                       }
                    },
                    "topic_evaluations":{}
                 },
                 "topic_evaluations":{}
              }
           }
        }
        """
        try:
            evaluation = mir_storage_ops.MirStorageOps.load_dataset_evaluations(
                mir_root=self.mir_root,
                mir_branch=self.branch_id,
                mir_task_id=self.task_id,
            )
        except errors.MirError:
            logging.exception("evaluation %s not found", self.branch_id)
            raise exceptions.DatasetEvaluationNotExists(f"evaluation {self.branch_id} not found")

        return evaluation
