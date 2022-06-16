from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import requests
from fastapi.logger import logger
from pydantic import BaseModel

from app.api.errors.errors import DatasetEvaluationNotFound, ModelNotFound, ModelNotReady
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
        annotations = [
            {
                "box": annotation["box"],
                "keyword": user_labels.get_main_names(annotation["class_id"])[0],
            }
            for annotation in res["annotations"]
        ]
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
        assets = [
            {
                "url": get_asset_url(asset["asset_id"]),
                "hash": asset["asset_id"],
                "keywords": user_labels.get_main_names(class_ids=asset["class_ids"]),
            }
            for asset in res["elements"]
        ]

        return cls(items=assets, total=res["total"])


@dataclass
class ModelMetaData:
    hash: str
    map: float
    task_parameters: str
    executor_config: str

    @classmethod
    def from_viz_res(cls, res: Dict) -> "ModelMetaData":
        return cls(res["model_id"], res["model_mAP"], res["task_parameters"], res["executor_config"])


class VizDataset(BaseModel):
    """
    Interface dataclass of VIZ output, defined as DatasetResult in doc:
    https://github.com/IndustryEssentials/ymir/blob/master/ymir/backend/src/ymir_viz/doc/ymir_viz_API.yaml
    """

    total_images_cnt: int
    class_ids_count: Dict[int, int]
    ignored_labels: Dict[str, int]
    negative_info: Dict[str, int]
    gt: Dict
    pred: Dict
    hist: Dict
    total_asset_mbytes: int
    total_assets_cnt: int


@dataclass
class DatasetMetaData:
    keywords: Dict[str, int]
    ignored_keywords: Dict[str, int]
    negative_info: Dict[str, int]
    asset_count: int
    keyword_count: int
    total_asset_mbytes: int
    total_assets_cnt: int
    annos_cnt: int
    ave_annos_cnt: float
    positive_asset_cnt: int
    negative_asset_cnt: int
    asset_bytes: List[Dict]
    asset_area: List[Dict]
    asset_quality: List[Dict]
    asset_hw_ratio: List[Dict]
    anno_area_ratio: List[Dict]
    anno_quality: List[Dict]
    class_names_count: Dict[str, int]

    @classmethod
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "DatasetMetaData":
        # for compatible
        res["total_images_cnt"] = res["pred"]["total_images_cnt"]
        res["class_ids_count"] = res["pred"]["class_ids_count"]
        res["ignored_labels"] = res["pred"]["ignored_labels"]
        res["negative_info"] = res["pred"]["negative_info"]
        viz_dataset = VizDataset(**res)
        keywords = {
            user_labels.get_main_names(class_id)[0]: count for class_id, count in viz_dataset.class_ids_count.items()
        }
        return cls(
            keywords=keywords,
            ignored_keywords=viz_dataset.ignored_labels,
            negative_info=viz_dataset.negative_info,
            asset_count=viz_dataset.total_images_cnt,
            keyword_count=len(keywords),
            total_asset_mbytes=viz_dataset.total_asset_mbytes,
            total_assets_cnt=viz_dataset.total_assets_cnt,
            annos_cnt=viz_dataset.pred["annos_cnt"],
            ave_annos_cnt=(viz_dataset.pred["annos_cnt"] / viz_dataset.total_assets_cnt
                           if viz_dataset.total_assets_cnt else 0),
            positive_asset_cnt=viz_dataset.pred["positive_asset_cnt"],
            negative_asset_cnt=viz_dataset.pred["negative_asset_cnt"],
            asset_bytes=viz_dataset.hist["asset_bytes"][0],
            asset_area=viz_dataset.hist["asset_area"][0],
            asset_quality=viz_dataset.hist["asset_quality"][0],
            asset_hw_ratio=viz_dataset.hist["asset_hw_ratio"][0],
            anno_area_ratio=viz_dataset.pred["hist"]["anno_area_ratio"][0],
            anno_quality=viz_dataset.pred["hist"]["anno_quality"][0],
            class_names_count=viz_dataset.pred["class_names_count"]
        )


class EvaluationScore(BaseModel):
    ap: float
    ar: float
    fn: int
    fp: int
    tp: int


class VizDatasetEvaluation(BaseModel):
    ci_evaluations: Dict[int, EvaluationScore]  # class_id -> scores
    ci_averaged_evaluation: EvaluationScore


class VizDatasetEvaluationResult(BaseModel):
    """
    Interface dataclass of VIZ output, defined as DatasetEvaluationResult in doc:
    https://github.com/IndustryEssentials/ymir/blob/master/ymir/backend/src/ymir_viz/doc/ymir_viz_API.yaml
    """

    iou_evaluations: Dict[float, VizDatasetEvaluation]  # iou -> evaluation
    iou_averaged_evaluation: VizDatasetEvaluation


class VizClient:
    def __init__(self, *, host: str = settings.VIZ_HOST):
        self.host = host
        self.session = requests.Session()
        self._user_id = None  # type: Optional[str]
        self._project_id = None  # type: Optional[str]
        self._branch_id = None  # type: Optional[str]
        self._url_prefix = None  # type: Optional[str]

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
        self._url_prefix = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches/{self._branch_id}"  # noqa: E501

    def get_assets(
        self,
        *,
        keyword_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
        user_labels: UserLabels,
    ) -> Assets:
        url = f"{self._url_prefix}/assets"
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
        url = f"{self._url_prefix}/assets/{asset_id}"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            logger.error("[viz] failed to get asset info: %s", resp.content)
            return None
        res = resp.json()["result"]
        return asdict(Asset.from_viz_res(asset_id, res, user_labels))

    def get_model(self) -> ModelMetaData:
        url = f"{self._url_prefix}/models"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        return ModelMetaData.from_viz_res(res)

    def get_dataset(self, user_labels: UserLabels) -> DatasetMetaData:
        url = f"{self._url_prefix}/datasets"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viz] get_dataset response: %s", res)
        return DatasetMetaData.from_viz_res(res, user_labels)

    def get_evaluations(self, user_labels: UserLabels) -> Dict:
        url = f"{self._url_prefix}/evaluations"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        evaluations = {
            dataset_hash: VizDatasetEvaluationResult(**evaluation).dict() for dataset_hash, evaluation in res.items()
        }
        convert_class_id_to_keyword(evaluations, user_labels)
        return evaluations

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
            elif error_code == VizErrorCode.DATASET_EVALUATION_NOT_EXISTS:
                raise DatasetEvaluationNotFound()
        raise ModelNotReady()

    def close(self) -> None:
        self.session.close()


def get_asset_url(asset_id: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-assets/{asset_id}"


def convert_class_id_to_keyword(obj: Dict, user_labels: UserLabels) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "ci_evaluations":
                obj[key] = {user_labels.get_main_names(k)[0]: v for k, v in value.items()}
            else:
                convert_class_id_to_keyword(obj[key], user_labels)
