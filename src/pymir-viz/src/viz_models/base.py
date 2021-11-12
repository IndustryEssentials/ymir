import json
import threading
from typing import Dict

from src import config
from src.libs import utils, app_logger
from src.libs.cache import redis_cache
from src.viz_models import pb_reader


class BaseModel:
    def __init__(self, user_id: str, repo_id: str, branch_id: str):
        self.user_id = user_id
        self.repo_id = repo_id
        self.branch_id = branch_id

        self.cache_key = utils.gen_cache_key(user_id, repo_id, branch_id)

    def check_cache_existence(self) -> int:
        detail_existence = redis_cache.exists(f"{self.cache_key}:{config.ASSET_ID_DETAIL}")
        index_existence = redis_cache.exists(
            f"{self.cache_key}:{config.ASSETS_CLASS_ID_INDEX}:{config.ALL_INDEX_CLASSIDS}"
        )
        cache_status = redis_cache.get(f"{self.cache_key}:{config.CACHE_STATUS}")
        if cache_status and cache_status["flag"]:
            cache_flag = True
        else:
            cache_flag = False

        flag = detail_existence and index_existence and cache_flag

        return flag

    def get_assets_content_from_pb(self) -> Dict:
        assets_content = pb_reader.MirStorageLoader(
            config.SANDBOX_ROOT, self.user_id, self.repo_id, self.branch_id
        ).get_asset_content()

        return assets_content

    @classmethod
    @utils.time_it
    def set_cache(cls, asset_content: Dict, cache_key: str) -> None:
        """
        set cache to Redis
        hash xxx:detail {'asset_id': {'metadata': xxx, 'annotations': xxx, 'class_ids': xx}}
        list xxx:class_id ['asset_id',]
        str  xxx:class_ids_count "{3:44, }"
        """
        if redis_cache.get(f"{cache_key}:{config.CACHE_STATUS}"):
            app_logger.logger.info("Skip setting cache!!! The other thread is writing cache now")
            return

        app_logger.logger.info("start setting cache!!!")
        redis_cache.set(f"{cache_key}:{config.CACHE_STATUS}", {"flag": 0})
        with redis_cache.pipeline() as pipe:
            for asset_id, asset_id_detail in asset_content["asset_ids_detail"].items():
                pipe.hmset(f"{cache_key}:{config.ASSET_ID_DETAIL}", {asset_id: json.dumps(asset_id_detail)})
            pipe.execute()

        with redis_cache.pipeline() as pipe:
            for class_id, assets_list in asset_content["class_ids_index"].items():
                pipe.lpush(f"{cache_key}:{config.ASSETS_CLASS_ID_INDEX}:{class_id}", *assets_list["asset_ids"])
            pipe.execute()

        redis_cache.set(f"{cache_key}:{config.ASSETS_CLASS_IDS_COUNT}", asset_content["class_ids_count"])
        redis_cache.set(f"{cache_key}:{config.CACHE_STATUS}", {"flag": 1})
        app_logger.logger.info("finish setting cache!!!")

    @classmethod
    def trigger_cache_generator(cls, asset_content: Dict, cache_key: str) -> None:
        # async generate middle structure content cache
        consumer_task = threading.Thread(target=cls.set_cache, args=(asset_content, cache_key,))
        consumer_task.start()
