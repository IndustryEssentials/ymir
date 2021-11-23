import os
from typing import List, Dict

from google.protobuf import message as pb_message
from mir.tools import mir_storage_ops

from proto import backend_pb2
from src import config
from src.libs import utils


class MirStorageLoader:
    def __init__(self, sandbox_root: str, user_id: str, repo_id: str, branch_id: str):
        self.mir_root = os.path.join(sandbox_root, user_id, repo_id)
        self.branch_id = branch_id

    @utils.time_it
    def load_raw_message(self, mir_storages: List[pb_message.Message]) -> Dict:
        # using as_dict flag means already MessageToDict
        mir_raw_data = mir_storage_ops.MirStorageOps.load(mir_root=self.mir_root,
                                                          mir_branch=self.branch_id,
                                                          mir_storages=mir_storages,
                                                          as_dict=True)

        return mir_raw_data

    def get_tasks_content(self) -> Dict:
        raw_task_message = self.load_raw_message([backend_pb2.MirStorage.MIR_TASKS])

        return raw_task_message[backend_pb2.MirStorage.MIR_TASKS]

    def get_keywords_content(self) -> Dict:
        raw_keywords_message = self.load_raw_message([backend_pb2.MirStorage.MIR_KEYWORDS])

        return raw_keywords_message[backend_pb2.MirStorage.MIR_KEYWORDS]

    def format_mir_content(self, all_metadata: Dict, all_annotations: Dict, all_keywords: Dict) -> Dict:
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
        }
        """
        head_task_id = all_annotations["head_task_id"]
        annotations = all_annotations["task_annotations"][head_task_id].get("image_annotations", {})

        assets_detail = dict()
        # add all assets index into index_predifined_keyids, key is config.ALL_INDEX_CLASSIDS
        all_keywords["index_predifined_keyids"][config.ALL_INDEX_CLASSIDS] = dict(asset_ids=[])
        for asset_id, asset_id_metadata in all_metadata["attributes"].items():
            all_keywords["index_predifined_keyids"][config.ALL_INDEX_CLASSIDS]["asset_ids"].append(asset_id)

            # set unlabeled asset_id annotations to []
            asset_id_annotation = annotations.get(asset_id, [])

            keywords_asset_id = all_keywords["keywords"].get(asset_id, [])
            class_ids = keywords_asset_id["predifined_keyids"] if keywords_asset_id else []

            asset_id_annotation = asset_id_annotation["annotations"] if asset_id_annotation else asset_id_annotation
            asset_detail = dict(
                metadata=asset_id_metadata,
                annotations=asset_id_annotation,
                class_ids=class_ids,
            )
            assets_detail[asset_id] = asset_detail

        result = dict(
            asset_ids_detail=assets_detail,
            class_ids_index=all_keywords["index_predifined_keyids"],
            class_ids_count=all_keywords["predifined_keyids_cnt"],
        )

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
        }
        """
        raw_message = self.load_raw_message(
            [backend_pb2.MirStorage.MIR_ANNOTATIONS, backend_pb2.MirStorage.MIR_METADATAS])
        annotations_message = raw_message[backend_pb2.MirStorage.MIR_ANNOTATIONS]
        metadatas_message = raw_message[backend_pb2.MirStorage.MIR_METADATAS]
        keywords_message = self.get_keywords_content()

        result = self.format_mir_content(metadatas_message, annotations_message, keywords_message)

        return result
