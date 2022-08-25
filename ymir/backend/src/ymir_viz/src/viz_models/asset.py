import logging
import threading
from typing import Dict, List, Optional, Set

import json

from src.config import viz_settings
from src.libs import utils
from src.libs.cache import redis_cache
from src.viz_models import pb_reader


class AssetsModel:
    def __init__(self, user_id: str, repo_id: str, branch_id: str):
        self.user_id = user_id
        self.repo_id = repo_id
        self.branch_id = branch_id

        self.redis_key_prefix = f"{user_id}_{repo_id}_{branch_id}:{viz_settings.VIZ_MIDDLE_VERSION}"
        self.key_asset_detail = f"{self.redis_key_prefix}:{viz_settings.VIZ_KEY_ASSET_DETAIL}"
        self.key_asset_index = f"{self.redis_key_prefix}:{viz_settings.VIZ_KEY_ASSET_INDEX}"
        self.key_cache_status = f"{self.redis_key_prefix}:{viz_settings.VIZ_CACHE_STATUS}"

    def check_cache_existence(self) -> int:
        detail_existence = redis_cache.exists(self.key_asset_detail)
        all_index_key = f"{self.key_asset_index}:{viz_settings.VIZ_ALL_INDEX_CLASSIDS}"
        index_existence = redis_cache.exists(all_index_key)
        cache_status = redis_cache.get(self.key_cache_status)
        if cache_status.get("flag"):
            cache_flag = True
        else:
            cache_flag = False

        flag = detail_existence and index_existence and cache_flag

        return flag

    @classmethod
    @utils.time_it
    def set_asset_content_cache(
        cls,
        asset_content: Dict,
        key_asset_detail: str,
        key_asset_index: str,
        key_cache_status: str,
    ) -> None:
        """
        set cache to Redis
        hash xxx:detail {'asset_id': {'metadata': xxx, 'gt': xxx, 'pred': xxx, 'class_ids': xx}}
        list xxx:class_id ['asset_id',]
        str  xxx:class_ids_count "{3:44, }"
        str  xxx:class_names_count "{'cat':44, }"
        str  xxx:ignored_labels "{'cat':5, }"
        str  xxx:negative_info "{
                "negative_images_cnt": 0,
                "project_negative_images_cnt": 0}"
        str  xxx:total_images_cnt "1"
        """
        if redis_cache.get(key_cache_status):
            logging.info(f"Skip setting cache {key_asset_detail}, The other thread is writing cache now")
            return

        logging.info(f"start setting cache {key_asset_detail}")
        redis_cache.set(key_cache_status, {"flag": 0})
        with redis_cache.pipeline() as pipe:
            for asset_id, asset_id_detail in asset_content["asset_ids_detail"].items():
                pipe.hset(name=key_asset_detail, mapping={asset_id: json.dumps(asset_id_detail)})
            pipe.execute()

        with redis_cache.pipeline() as pipe:
            cid_to_assets = asset_content["class_ids_index"]
            for class_id, assets_list in cid_to_assets.items():
                if assets_list:
                    pipe.rpush(f"{key_asset_index}:{class_id}", *assets_list)

            cid_to_assets = asset_content["pred_class_ids_index"]
            for class_id, assets_list in cid_to_assets.items():
                if assets_list:
                    pipe.rpush(f"{key_asset_index}:pred:{class_id}", *assets_list)

            cid_to_assets = asset_content["gt_class_ids_index"]
            for class_id, assets_list in cid_to_assets.items():
                if assets_list:
                    pipe.rpush(f"{key_asset_index}:gt:{class_id}", *assets_list)

            pipe.execute()

        redis_cache.set(key_cache_status, {"flag": 1})
        logging.info("finish setting cache!!!")

    def trigger_cache_generator(self, asset_content: Dict) -> None:
        # async generate middle structure content cache
        consumer_task = threading.Thread(
            target=self.set_asset_content_cache,
            args=(
                asset_content,
                self.key_asset_detail,
                self.key_asset_index,
                self.key_cache_status,
            ),
        )
        consumer_task.start()

    @classmethod
    def format_assets_info(cls, assets_content: Dict, offset: int, limit: int, class_id: int) -> Dict:
        """
        return structure like this:
        {
            'elements': [{'asset_id':xxx, 'class_ids':[2,3]},],
            'limit': 3,
            'offset': 1,
            'total': 234
        }
        """
        asset_ids = assets_content["class_ids_index"][class_id][offset:limit + offset]
        elements = []
        for asset_id in asset_ids:
            elements.append({
                "asset_id": asset_id,
                "class_ids": assets_content["asset_ids_detail"][asset_id]["class_ids"],
                "metadata": assets_content["asset_ids_detail"][asset_id]["metadata"],
                "pred": assets_content["asset_ids_detail"][asset_id]["pred"],
                "gt": assets_content["asset_ids_detail"][asset_id]["gt"],
            })

        result = dict(
            elements=elements,
            limit=limit,
            offset=offset,
            total=len(assets_content["class_ids_index"][class_id]),
        )

        return result

    def get_assets_info_from_cache(self, offset: int, limit: int, class_id: int) -> Dict:
        """
        return structure like this:
        {
            'elements': [{'asset_id':xxx, 'class_ids':[2,3], 'gt': [], 'pred': [], 'metadata': []},],
            'limit': 3,
            'offset': 1,
            'total': 234
        }
        """
        asset_ids = redis_cache.lrange(f"{self.key_asset_index}:{class_id}", offset, offset + limit - 1)
        assets_detail = redis_cache.hmget(self.key_asset_detail, asset_ids)

        elements = []
        for asset_id, asset_detail in zip(asset_ids, assets_detail):
            asset_detail = json.loads(asset_detail)
            elements.append(
                {
                    "asset_id": asset_id,
                    "class_ids": asset_detail["class_ids"],
                    "gt": asset_detail["gt"],
                    "pred": asset_detail["pred"],
                    "metadata": asset_detail["metadata"],
                }
            )
        total = redis_cache.llen(f"{self.key_asset_index}:{class_id}")
        result = dict(elements=elements, limit=limit, offset=offset, total=total)

        return result

    @utils.time_it
    def get_assets_info(self, offset: int, limit: int, class_id: int) -> Dict:
        """
        example return data:
        [{
            'asset_id': 'abc',
            'pred': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2}],
            'gt': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2}],
            'class_ids': [2, 30],
            'metadata': {'asset_type': 1, 'height': 375, 'image_channels': 3, 'timestamp': {'start': 123}, 'width': 500}
        }]
        """
        class_id = class_id if class_id is not None else viz_settings.VIZ_ALL_INDEX_CLASSIDS

        if self.check_cache_existence():
            result = self.get_assets_info_from_cache(offset=offset, limit=limit, class_id=class_id)
            logging.info("get_assets_info from cache")
        else:
            assets_content = pb_reader.MirStorageLoader(
                sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
                user_id=self.user_id,
                repo_id=self.repo_id,
                branch_id=self.branch_id,
                task_id=self.branch_id,
            ).get_assets_content()
            result = self.format_assets_info(
                assets_content=assets_content, offset=offset, limit=limit, class_id=class_id
            )

            # asynchronous generate cache content,and we can add some policy to trigger it later
            self.trigger_cache_generator(assets_content)

        return result

    def get_dataset_stats_from_cache(self, cis: List[int]) -> dict:
        def _gen_key(is_gt: bool, ci: int) -> str:
            if not is_gt:
                return f"{self.key_asset_index}:pred:{ci}"
            else:
                return f"{self.key_asset_index}:gt:{ci}"

        def _gen_stats_result(all_asset_ids: Set[str], is_gt: bool, cis: List[int]) -> dict:
            class_id_to_asset_cnt: Dict[int, int] = {}  # key: class id, value: count of assets
            positive_asset_ids: Set[str] = set()

            for ci in cis:
                ci_cache_key = _gen_key(is_gt=is_gt, ci=ci)
                if not redis_cache.exists(ci_cache_key):
                    class_id_to_asset_cnt[ci] = 0
                    continue

                ci_asset_ids = redis_cache.lrange(ci_cache_key, 0, -1)
                class_id_to_asset_cnt[ci] = len(ci_asset_ids)
                positive_asset_ids.update(ci_asset_ids)

            return {
                'negative_assets_count': len(all_asset_ids - positive_asset_ids),
                'class_ids_count': class_id_to_asset_cnt,
            }

        all_asset_ids = set(self.get_all_asset_ids_from_cache())
        pred_stats = _gen_stats_result(all_asset_ids=all_asset_ids, is_gt=False, cis=cis)
        gt_stats = _gen_stats_result(all_asset_ids=all_asset_ids, is_gt=True, cis=cis)

        return {
            'total_assets_count': len(all_asset_ids),
            'pred': pred_stats,
            'gt': gt_stats,
        }

    def get_dataset_stats(self, cis: List[int]) -> dict:
        def _gen_stats_result(assets_content: dict, is_gt: bool, cis: List[int]) -> dict:
            class_ids_index: Dict[int, List[str]] = assets_content[
                'pred_class_ids_index'] if not is_gt else assets_content['gt_class_ids_index']

            class_id_to_asset_cnt: Dict[int, int] = {}  # key: class id, value: count of assets
            positive_asset_ids: Set[str] = set()

            for ci in cis:
                if ci not in class_ids_index:
                    class_id_to_asset_cnt[ci] = 0
                    continue

                ci_asset_ids = class_ids_index[ci]
                class_id_to_asset_cnt[ci] = len(ci_asset_ids)
                positive_asset_ids.update(ci_asset_ids)

            return {
                'negative_assets_count': len(set(assets_content['all_asset_ids']) - positive_asset_ids),
                'class_ids_count': class_id_to_asset_cnt,
            }

        if self.check_cache_existence():
            logging.info("get_dataset_stats_from_cache")

            return self.get_dataset_stats_from_cache(cis=cis)

        # get result from mir_storage_ops
        assets_content = pb_reader.MirStorageLoader(
            sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
            user_id=self.user_id,
            repo_id=self.repo_id,
            branch_id=self.branch_id,
            task_id=self.branch_id,
        ).get_assets_content()

        pred_stats = _gen_stats_result(assets_content=assets_content, is_gt=False, cis=cis)
        gt_stats = _gen_stats_result(assets_content=assets_content, is_gt=True, cis=cis)

        self.trigger_cache_generator(assets_content)

        return {
            'total_assets_count': len(assets_content['all_asset_ids']),
            'pred': pred_stats,
            'gt': gt_stats,
        }

    def get_all_asset_ids_from_cache(self) -> List[str]:
        class_id = viz_settings.VIZ_ALL_INDEX_CLASSIDS
        return redis_cache.lrange(f"{self.key_asset_index}:{class_id}", 0, -1)

    @utils.time_it
    def get_all_asset_ids(self) -> List[str]:
        # take the shortcut if dataset has been cached
        if self.check_cache_existence():
            logging.info("get_all_asset_ids from cache")
            return self.get_all_asset_ids_from_cache()

        # otherwise, ONLY read metadata.mir to save time
        dataset_metadata = pb_reader.MirStorageLoader(
            sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
            user_id=self.user_id,
            repo_id=self.repo_id,
            branch_id=self.branch_id,
            task_id=self.branch_id,
        ).get_dataset_metadata()
        return list(dataset_metadata["attributes"].keys())

    @utils.time_it
    def get_asset_id_info(self, asset_id: str) -> Optional[Dict]:
        """
        example return data:
        {
            'asset_id': 'abc',
            'pred': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2, 'cm': 1}],
            'gt': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2, 'cm': 1}],
            'class_ids': [2, 30],
            'metadata': {'asset_type': 1, 'height': 375, 'image_channels': 3, 'timestamp': {'start': 123}, 'width': 500}
        }

        cm: mir_command.proto.ConfusionMatrixType
        """
        if self.check_cache_existence():
            result = redis_cache.hget(self.key_asset_detail, asset_id)
            logging.info(f"get_asset_id: {asset_id} from cache")
        else:
            assets_content = pb_reader.MirStorageLoader(
                sandbox_root=viz_settings.BACKEND_SANDBOX_ROOT,
                user_id=self.user_id,
                repo_id=self.repo_id,
                branch_id=self.branch_id,
                task_id=self.branch_id,
            ).get_assets_content()
            result = assets_content["asset_ids_detail"][asset_id]

            # asynchronous generate cache content,and we can add some policy to trigger it later
            self.trigger_cache_generator(assets_content)

        result["asset_id"] = asset_id
        return result
