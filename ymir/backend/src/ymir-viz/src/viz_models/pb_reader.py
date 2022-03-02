import os
from typing import Dict, Tuple

from mir.tools import mir_storage_ops, errors

from src import config
from src.libs import utils, exceptions, app_logger


class MirStorageLoader:
    def __init__(self, sandbox_root: str, user_id: str, repo_id: str, branch_id: str):
        self.mir_root = os.path.join(sandbox_root, user_id, repo_id)
        self.branch_id = branch_id

    @utils.time_it
    def get_branch_contents(self) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
        # using as_dict flag means already MessageToDict
        try:
            (
                metadatas,
                annotations,
                keywords,
                tasks,
                statistic_info,
            ) = mir_storage_ops.MirStorageOps.load_branch_contents(mir_root=self.mir_root, mir_branch=self.branch_id)
        # TODO: command define
        except ValueError as e:
            app_logger.logger.error(e)
            raise exceptions.BranchNotExists(f"branch {self.branch_id} not exist from ymir command")

        return metadatas, annotations, keywords, tasks, statistic_info

    def get_model_info(self) -> Dict:
        try:
            model_info = mir_storage_ops.MirStorageOps.load_single_model(
                mir_root=self.mir_root, mir_branch=self.branch_id
            )
        except errors.MirError:
            raise exceptions.ModelNotExists(f"model {self.branch_id} not found")

        return model_info

    def format_mir_content(
        self, all_tasks_info: Dict, all_metadata: Dict, all_annotations: Dict, all_keywords: Dict, statistic_info: Dict
    ) -> Dict:
        """
        return like this structure
        {
            "asset_ids_detail": {
                "asset_id": {
                    "metadata": {"asset_type": 2, "width": 1080, "height": 1620,},
                    "annotations": [{"box": {"x": 26, "y": 189, "w": 19, "h": 50}, "class_id": 2}],
                    "class_ids": [2, 3],
                }
            },
            "class_ids_index": {3: ["asset_id",], "class_ids_count": {3: 34}},
            "ignored_labels": {'cat':5, },
        }
        """
        app_logger.logger.warning('55555555555555555555555555555')
        head_task_id = all_annotations["head_task_id"]
        annotations = all_annotations["task_annotations"][head_task_id].get("image_annotations", {})

        assets_detail = dict()
        # add all assets index into index_predifined_keyids, key is config.ALL_INDEX_CLASSIDS
        all_keywords["index_predifined_keyids"][config.ALL_INDEX_CLASSIDS] = dict(asset_ids=[])
        for asset_id, asset_id_metadata in all_metadata["attributes"].items():
            all_keywords["index_predifined_keyids"][config.ALL_INDEX_CLASSIDS]["asset_ids"].append(asset_id)

            # set unlabeled asset_id annotations to []
            asset_id_annotation = annotations.get(asset_id, [])
            app_logger.logger.warning('444444444444444444444444444444')
            keywords_asset_id = all_keywords["keywords"].get(asset_id, [])
            class_ids = keywords_asset_id["predifined_keyids"] if keywords_asset_id else []
            app_logger.logger.warning('33333333333333333333333333333333')
            asset_id_annotation = asset_id_annotation["annotations"] if asset_id_annotation else asset_id_annotation
            asset_detail = dict(metadata=asset_id_metadata, annotations=asset_id_annotation, class_ids=class_ids,)
            assets_detail[asset_id] = asset_detail
        app_logger.logger.warning('22222222222222222222222222222222222222')
        app_logger.logger.warning(statistic_info)
        app_logger.logger.warning(all_keywords)
        result = dict(
            asset_ids_detail=assets_detail,
            class_ids_index=all_keywords["index_predifined_keyids"],
            class_ids_count=statistic_info["predefined_keyids_cnt"],
            negative_info=dict(
                negative_images_cnt=statistic_info["negative_images_cnt"],
                project_negative_images_cnt=statistic_info["project_negative_images_cnt"],
            ),
            ignored_labels=all_tasks_info["tasks"][self.branch_id].get("unknown_types", {}),
        )
        app_logger.logger.warning(result)
        return result

    def get_asset_content(self) -> Dict:
        """
        return like this structure
        {
            "asset_ids_detail": {
                "asset_id": {
                    "metadata": {"asset_type": 2, "width": 1080, "height": 1620,},
                    "annotations": [{"box": {"x": 26, "y": 189, "w": 19, "h": 50}, "class_id": 2}],
                    "class_ids": [2, 3],
                }
            },
            "class_ids_index": {3: ["asset_id",], "class_ids_count": {3: 34}},
            "ignored_labels": {'cat':5},
        }
        """
        app_logger.logger.warning('6666666666666666666666666666666')
        metadatas, annotations, keywords, tasks, statistic_info = self.get_branch_contents()
        result = self.format_mir_content(tasks, metadatas, annotations, keywords, statistic_info)

        app_logger.logger.warning(result)

        return result
