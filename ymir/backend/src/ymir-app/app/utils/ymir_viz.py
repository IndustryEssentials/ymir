from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import requests
from fastapi.logger import logger
from id_definition.error_codes import VizErrorCode

from app.api.errors.errors import ModelNotFound, ModelNotReady
from app.config import settings


@dataclass
class Asset:
    url: str
    hash: str
    annotations: List[Dict]
    keywords: List[str]
    metadata: Dict

    @classmethod
    def from_viz_res(
        cls, asset_id: str, res: Dict, keyword_id_to_name: Dict[int, str]
    ) -> "Asset":
        annotations = [
            {
                "box": annotation["box"],
                "keyword": keyword_id_to_name.get(int(annotation["class_id"])),
            }
            for annotation in res["annotations"]
        ]
        keywords = [
            keyword_id_to_name.get(int(class_id)) for class_id in res["class_ids"]
        ]
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
    total: int
    items: List
    keywords: Dict[str, int]
    ignored_keywords: Dict[str, int]
    negative_info: Dict[str, int]

    @classmethod
    def from_viz_res(cls, res: Dict, keyword_id_to_name: Dict) -> "Assets":
        assets = [
            {
                "url": get_asset_url(asset["asset_id"]),
                "hash": asset["asset_id"],
                "keywords": [
                    keyword_id_to_name[int(class_id)]
                    for class_id in asset["class_ids"]
                    if int(class_id) in keyword_id_to_name
                ],
            }
            for asset in res["elements"]
        ]

        keywords = {
            keyword_id_to_name[int(class_id)]: count
            for class_id, count in res["class_ids_count"].items()
            if int(class_id) in keyword_id_to_name
        }
        ignored_keywords = res["ignored_labels"]
        negative_info = res["negative_info"]
        return cls(res["total"], assets, keywords, ignored_keywords, negative_info)


@dataclass
class Model:
    hash: str
    map: float

    @classmethod
    def from_viz_res(cls, res: Dict) -> "Model":
        return cls(res["model_id"], res["model_mAP"])


class VizClient:
    def __init__(self, *, host: str):
        self.host = host
        self.session = requests.Session()
        self._user_id = None  # type: Optional[str]
        self._project_id = None  # type: Optional[str]
        self._branch_id = None  # type: Optional[str]
        self._keyword_id_to_name = None  # type: Optional[Dict]

    def config(
        self,
        *,
        user_id: int,
        project_id: int,
        branch_id: str,
        keyword_id_to_name: Optional[Dict] = None,
    ) -> None:
        self._user_id = f"{user_id:0>4}"
        self._project_id = f"{project_id:0>6}"
        self._branch_id = branch_id
        self._keyword_id_to_name = keyword_id_to_name

    def get_assets(
        self,
        *,
        keyword_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Assets:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/assets"  # noqa: E501

        payload = {"class_id": keyword_id, "limit": limit, "offset": offset}
        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            resp.raise_for_status()
        res = resp.json()["result"]
        logger.info("[viz] get_assets response: %s", res)
        assert self._keyword_id_to_name is not None, "ymir_viz not configured"
        return Assets.from_viz_res(res, self._keyword_id_to_name)

    def get_asset(
        self,
        *,
        asset_id: str,
    ) -> Optional[Dict]:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/assets/{asset_id}"  # noqa: E501

        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            return None
        res = resp.json()["result"]
        assert self._keyword_id_to_name is not None, "ymir_viz not configured"
        return asdict(Asset.from_viz_res(asset_id, res, self._keyword_id_to_name))

    def get_model(self) -> Dict:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}/models"  # noqa: E501
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        return asdict(Model.from_viz_res(res))

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
            error_code = resp.json()["code"]
            if error_code == VizErrorCode.MODEL_NOT_EXISTS:
                raise ModelNotFound()
        raise ModelNotReady()

    def close(self) -> None:
        self.session.close()


def get_asset_url(asset_id: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-assets/{asset_id}"
