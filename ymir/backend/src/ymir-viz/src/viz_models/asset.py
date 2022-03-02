import json
from typing import Dict, Union

from src import config
from src.libs import utils, app_logger
from src.libs.cache import redis_cache
from src.viz_models.base import BaseModel


class Asset(BaseModel):
    @classmethod
    @utils.time_it
    def format_assets_info(cls, assets_content: Dict, offset: int, limit: int, class_id: int) -> Dict:
        """
        return structure like this:
        {'class_ids_count': {3: 34}, 'elements': [{'asset_id':xxx, 'class_ids':[2,3]},],
        'limit': 3, offset: 1, total: 234}
        """
        asset_ids = assets_content["class_ids_index"][class_id]["asset_ids"][offset:limit + offset]
        elements = [
            dict(asset_id=asset_id, class_ids=assets_content["asset_ids_detail"][asset_id]["class_ids"])
            for asset_id in asset_ids
        ]

        result = dict(
            class_ids_count=assets_content["class_ids_count"],
            ignored_labels=assets_content["ignored_labels"],
            negative_info=assets_content["negative_info"],
            elements=elements,
            limit=limit,
            offset=offset,
            total=len(assets_content["class_ids_index"][class_id]["asset_ids"]),
        )

        return result

    @classmethod
    def get_assets_info_from_cache(cls, cache_key: str, offset: int, limit: int, class_id: int) -> Dict:
        """
        return structure like this:
        {'class_ids_count': {3: 34}, 'elements': [{'asset_id':xxx, 'class_ids':[2,3]},],
        'limit': 3, offset: 1, total: 234}
        """
        asset_ids = redis_cache.lrange(f"{cache_key}:{config.ASSETS_CLASS_ID_INDEX}:{class_id}", offset,
                                       offset + limit - 1)
        assets_detail = redis_cache.hmget(f"{cache_key}:{config.ASSET_ID_DETAIL}", asset_ids)

        elements = []
        for asset_id, asset_detail in zip(asset_ids, assets_detail):
            elements.append(dict(asset_id=asset_id, class_ids=json.loads(asset_detail)["class_ids"]))
        assets_attributes = redis_cache.get(f"{cache_key}:{config.ASSETS_ATTRIBUTES}")
        total = redis_cache.llen(f"{cache_key}:{config.ASSETS_CLASS_ID_INDEX}:{class_id}")

        result = dict(
            class_ids_count=assets_attributes["class_ids_count"],
            ignored_labels=assets_attributes["ignored_labels"],
            negative_info=assets_attributes["negative_info"],
            elements=elements,
            limit=limit,
            offset=offset,
            total=total,
        )

        return result

    @utils.time_it
    def get_assets_info(self, offset: int, limit: int, class_id: int) -> Dict:
        app_logger.logger.warning("9999999999999999999999999999999999999999999")
        class_id = class_id if class_id is not None else config.ALL_INDEX_CLASSIDS

        if self.check_cache_existence():
            app_logger.logger.warning("888888888888888888888888888888888")
            result = self.get_assets_info_from_cache(self.cache_key, offset, limit, class_id)
            app_logger.logger.info("get_assets_info from cache")
        else:
            app_logger.logger.warning("7777777777777777777777777777777777")
            assets_content = self.get_assets_content_from_pb()
            app_logger.logger.warning(assets_content)
            result = self.format_assets_info(assets_content, offset, limit, class_id)

            # asynchronous generate cache content,and we can add some policy to trigger it later
            self.trigger_cache_generator(assets_content, self.cache_key)

        return result

    @classmethod
    def get_asset_id_info_from_cache(cls, cache_key: str, asset_id: str) -> Union[Dict, None]:
        """
        return like this structure
        {'annotations': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2}], 'class_ids': [2, 30],
        'metadata': {'asset_type': 1, 'height': 375, 'image_channels': 3, 'timestamp': {'start': 123}, 'width': 500}}
        """
        asset_id_info = redis_cache.hget(f"{cache_key}:{config.ASSET_ID_DETAIL}", asset_id)

        return asset_id_info

    @classmethod
    @utils.time_it
    def format_asset_id_info(cls, asset_id: str, assets_content: Dict) -> Dict:
        """
        return like this structure
        {'annotations': [{'box': {'h': 329, 'w': 118, 'x': 1, 'y': 47}, 'class_id': 2}], 'class_ids': [2, 30],
        'metadata': {'asset_type': 1, 'height': 375, 'image_channels': 3, 'timestamp': {'start': 123}, 'width': 500}}
        """
        result = assets_content["asset_ids_detail"][asset_id]

        return result

    @utils.time_it
    def get_asset_id_info(self, asset_id: str) -> Union[Dict, None]:
        if self.check_cache_existence():
            result = self.get_asset_id_info_from_cache(self.cache_key, asset_id)
            app_logger.logger.info(f"get_asset_id: {asset_id} from cache")
        else:
            assets_content = self.get_assets_content_from_pb()
            result = self.format_asset_id_info(asset_id, assets_content)

            # asynchronous generate cache content,and we can add some policy to trigger it later
            self.trigger_cache_generator(assets_content, self.cache_key)

        return result
