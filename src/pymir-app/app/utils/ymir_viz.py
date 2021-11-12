from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import requests

from app.config import settings
from app.utils.class_ids import CLASS_TYPES, REVERSED_CLASS_TYPES


@dataclass
class Asset:
    url: str
    hash: str
    annotations: List[Dict]
    keywords: List[str]
    metadata: Dict

    @classmethod
    def from_viz_res(cls, asset_id: str, res: Dict) -> "Asset":
        annotations = [
            {
                "box": annotation["box"],
                "keyword": CLASS_TYPES[int(annotation["class_id"])],
            }
            for annotation in res["annotations"]
        ]
        keywords = [CLASS_TYPES[int(class_id)] for class_id in res["class_ids"]]
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
            keywords,
            metadata,
        )


@dataclass
class Assets:
    total: int
    items: List
    keywords: Dict[str, int]

    @classmethod
    def from_viz_res(cls, res: Dict) -> "Assets":
        assets = [
            {
                "url": get_asset_url(asset["asset_id"]),
                "hash": asset["asset_id"],
                "keywords": [
                    CLASS_TYPES[int(class_id)] for class_id in asset["class_ids"]
                ],
            }
            for asset in res["elements"]
        ]

        # todo
        #  better way to map to keyword_name
        keywords = {
            CLASS_TYPES[int(class_id)]: count
            for class_id, count in res["class_ids_count"].items()
        }

        return cls(res["total"], assets, keywords)


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

    def get_assets(
        self,
        *,
        user_id: int,
        repo_id: Optional[str] = None,
        branch_id: str,
        keyword: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Assets:
        _user_id = f"{user_id:0>4}"
        repo_id = repo_id or f"{user_id:0>6}"
        url = f"http://{self.host}/v1/users/{_user_id}/repositories/{repo_id}/branches/{branch_id}/assets"

        # todo
        #  better way to map to keyword_id
        keyword_id = REVERSED_CLASS_TYPES[keyword] if keyword else None
        payload = {"class_id": keyword_id, "limit": limit, "offset": offset}
        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            resp.raise_for_status()
        res = resp.json()["result"]
        return Assets.from_viz_res(res)

    def get_asset(
        self,
        *,
        user_id: int,
        repo_id: Optional[str] = None,
        branch_id: str,
        asset_id: str,
    ) -> Optional[Dict]:
        _user_id = f"{user_id:0>4}"
        repo_id = repo_id or f"{_user_id:0>6}"
        url = f"http://{self.host}/v1/users/{_user_id}/repositories/{repo_id}/branches/{branch_id}/assets/{asset_id}"

        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            return None
        res = resp.json()["result"]
        return asdict(Asset.from_viz_res(asset_id, res))

    def get_model(
        self,
        *,
        user_id: int,
        repo_id: Optional[str] = None,
        branch_id: str,
    ) -> Optional[Dict]:
        _user_id = f"{user_id:0>4}"
        repo_id = repo_id or f"{_user_id:0>6}"
        url = f"http://{self.host}/v1/users/{_user_id}/repositories/{repo_id}/branches/{branch_id}/models"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            return None
        res = resp.json()["result"]
        return asdict(Model.from_viz_res(res))

    def close(self) -> None:
        self.session.close()


def get_asset_url(asset_id: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-assets/{asset_id}"
