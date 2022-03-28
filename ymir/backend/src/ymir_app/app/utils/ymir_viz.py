from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import requests
from fastapi.logger import logger

from app.api.errors.errors import ModelNotFound, ModelNotReady
from app.config import settings
from common_utils.labels import UserLabels
from id_definition.error_codes import VizErrorCode


@dataclass
class Asset:
    url: str
    hash: str
    annotations: List[Dict]
    keywords: List[str]
    metadata: Dict

    @classmethod
    def from_viz_res(cls, asset_id: str, res: Dict, user_labels: UserLabels) -> "Asset":
        annotations = [{
            "box": annotation["box"],
            "keyword": user_labels.get_main_names(annotation["class_id"])[0],
        } for annotation in res["annotations"]]
        keywords = user_labels.get_main_names(class_ids=res["class_ids"])
        keywords = list(filter(None, keywords))
        metadata = {
            "height": res["metadata"]["height"],
            "width": res["metadata"]["width"],
            "channel": res["metadata"]["image_channels"],
            "timestamp": int(res["metadata"]["timestamp"]["start"]),
        }
        return cls(
            get_asset_url(asset_id),
            asset_id,
            annotations,
            keywords,  # type: ignore
            metadata,
        )


@dataclass
class Assets:
    items: List
    total: int

    @classmethod
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "Assets":
        assets = [{
            "url": get_asset_url(asset["asset_id"]),
            "hash": asset["asset_id"],
            "keywords": user_labels.get_main_names(class_ids=asset["class_ids"]),
        } for asset in res["elements"]]

        return cls(items=assets, total=res["total"])


@dataclass
class Model:
    hash: str
    map: float
    task_parameters: str
    executor_config: str

    @classmethod
    def from_viz_res(cls, res: Dict) -> "Model":
        return cls(res["model_id"], res["model_mAP"], res["task_parameters"], res["executor_config"])


@dataclass
class VizDataset():
    """
    Interface dataclass of VIZ output, defined as DatasetResult in doc:
    https://github.com/IndustryEssentials/ymir/blob/master/ymir/backend/src/ymir-viz/doc/ymir_viz_API.yaml
    """
    total_images_cnt: int
    class_names_count: Dict[str, int]
    ignored_labels: Dict[str, int]
    negative_info: Dict[str, int]

    def to_app_dataset(self, user_labels: UserLabels) -> 'AppDataset':
        return AppDataset(total=self.total_images_cnt,
                          keywords=self.class_names_count,
                          ignored_keywords=self.ignored_labels,
                          negative_info=self.negative_info)


@dataclass
class AppDataset():
    total: int
    keywords: Dict[str, int]
    ignored_keywords: Dict[str, int]
    negative_info: Dict[str, int]

    @classmethod
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "AppDataset":
        return VizDataset(**res).to_app_dataset(user_labels)


class VizClient:
    def __init__(self, *, host: str = settings.VIZ_HOST):
        self.host = host
        self.session = requests.Session()
        self._user_id = None  # type: Optional[str]
        self._project_id = None  # type: Optional[str]
        self._branch_id = None  # type: Optional[str]

    def initialize(
        self,
        *,
        user_id: int,
        project_id: int,
        branch_id: str,
    ) -> None:
        self._user_id = f"{user_id:0>4}"
        self._project_id = f"{project_id:0>6}"
        self._branch_id = branch_id

    def get_assets(
        self,
        *,
        keyword_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
        user_labels: UserLabels,
    ) -> Assets:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/assets"  # noqa: E501

        payload = {"class_id": keyword_id, "limit": limit, "offset": offset}
        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            logger.error("[viz] failed to get assets info: %s", resp.content)
            resp.raise_for_status()
        res = resp.json()["result"]
        logger.info("[viz] get_assets response: %s", res)
        return Assets.from_viz_res(res, user_labels)

    def get_asset(
        self,
        *,
        asset_id: str,
        user_labels: UserLabels,
    ) -> Optional[Dict]:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/assets/{asset_id}"  # noqa: E501

        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            logger.error("[viz] failed to get asset info: %s", resp.content)
            return None
        res = resp.json()["result"]
        return asdict(Asset.from_viz_res(asset_id, res, user_labels))

    def get_model(self) -> Dict:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/models"  # noqa: E501
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        return asdict(Model.from_viz_res(res))

    def get_dataset(self, user_labels: UserLabels) -> 'AppDataset':
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/datasets"  # noqa: E501
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        return AppDataset.from_viz_res(res, user_labels)

    def parse_resp(self, resp: requests.Response) -> Dict:
        """
        response falls in three categories:
        1. valid result
        2. task is finished, but model not exists
        3. model not ready, try to get model later
        """
        if resp.ok:
            return resp.json()["result"]
        elif resp.status_code == 400:
            logger.error("[viz] failed to get model info: %s", resp.content)
            error_code = resp.json()["code"]
            if error_code == VizErrorCode.MODEL_NOT_EXISTS:
                raise ModelNotFound()
        raise ModelNotReady()

    def close(self) -> None:
        self.session.close()


def get_asset_url(asset_id: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-assets/{asset_id}"
