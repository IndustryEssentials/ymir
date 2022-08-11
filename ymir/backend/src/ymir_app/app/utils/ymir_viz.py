from dataclasses import asdict, dataclass
import json
from typing import Any, Dict, List, Optional

import requests
from fastapi.logger import logger
from pydantic import BaseModel, validator

from app.api.errors.errors import (
    DatasetEvaluationNotFound,
    DatasetEvaluationMissingAnnotation,
    ModelNotFound,
    FailedToParseVizResponse,
)
from app.config import settings
from common_utils.labels import UserLabels
from id_definition.error_codes import VizErrorCode, CMDResponseCode


def parse_annotations(annotations: List[Dict], user_labels: UserLabels) -> List[Dict]:
    return [
        {
            "box": annotation["box"],
            "cm": annotation["cm"],
            "keyword": user_labels.get_main_name(annotation["class_id"]),
        }
        for annotation in annotations
    ]


@dataclass
class Asset:
    url: str
    hash: str
    keywords: List[str]
    metadata: Dict
    gt: List[Dict]
    pred: List[Dict]

    @classmethod
    def from_viz_res(cls, asset_id: str, res: Dict, user_labels: UserLabels) -> "Asset":
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
            keywords,  # type: ignore
            metadata,
            parse_annotations(res["gt"], user_labels),
            parse_annotations(res["pred"], user_labels),
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
                "metadata": asset["metadata"],
                "gt": parse_annotations(asset["gt"], user_labels),
                "pred": parse_annotations(asset["pred"], user_labels),
            }
            for asset in res["elements"]
        ]
        # fixme
        #  remove upon replacing all viz endpoints
        total = res.get("total") or res.get("total_assets_count") or 0
        return cls(items=assets, total=total)


@dataclass
class ModelMetaData:
    hash: str
    map: float
    task_parameters: str
    executor_config: str
    model_stages: dict
    best_stage_name: str
    keywords: Optional[str]

    @classmethod
    def from_viz_res(cls, res: Dict) -> "ModelMetaData":
        keywords = res["executor_config"].get("class_names")
        return cls(
            res["model_id"],
            res["model_mAP"],
            res["task_parameters"],
            res["executor_config"],
            res["model_stages"],
            res["best_stage_name"],
            json.dumps(keywords) if keywords else None,
        )


@dataclass
class DatasetAnnotationMetadata:
    keywords: Dict[str, int]
    class_ids_count: Dict[str, int]
    negative_assets_count: int

    tags_count_total: Dict
    tags_count: Dict

    hist: Dict

    annos_count: int
    ave_annos_count: float

    @classmethod
    def from_viz_res(cls, res: Dict, total_assets_count: int, user_labels: UserLabels) -> "DatasetAnnotationMetadata":
        ave_annos_count = round(res["annos_count"] / total_assets_count, 2) if total_assets_count else 0
        keywords = {
            user_labels.get_main_name(int(class_id)): count for class_id, count in res["class_ids_count"].items()
        }
        return cls(
            keywords=keywords,
            class_ids_count=res["class_ids_count"],
            negative_assets_count=res["negative_assets_count"],
            tags_count_total=res["tags_count_total"],
            tags_count=res["tags_count"],
            hist=res["hist"],
            annos_count=res["annos_count"],
            ave_annos_count=ave_annos_count,
        )


@dataclass
class DatasetMetaData:
    """
    Interface dataclass of VIZ output, defined as DatasetResult in doc:
    https://github.com/IndustryEssentials/ymir/blob/master/ymir/backend/src/ymir_viz/doc/ymir_viz_API.yaml
    """

    keywords: Dict
    keywords_updated: bool

    cks_count: Dict
    cks_count_total: Dict

    total_assets_mbytes: int
    total_assets_count: int

    gt: Optional[DatasetAnnotationMetadata]
    pred: Optional[DatasetAnnotationMetadata]
    hist: Dict

    negative_info: Dict[str, int]

    @classmethod
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "DatasetMetaData":
        total_assets_count = res["total_assets_count"]
        gt = (
            DatasetAnnotationMetadata.from_viz_res(res["gt"], total_assets_count, user_labels)
            if res.get("gt")
            else None
        )
        pred = (
            DatasetAnnotationMetadata.from_viz_res(res["pred"], total_assets_count, user_labels)
            if res.get("pred")
            else None
        )
        hist = {
            "asset_bytes": res["hist"]["asset_bytes"],
            "asset_area": res["hist"]["asset_area"],
            "asset_quality": res["hist"]["asset_quality"],
            "asset_hw_ratio": res["hist"]["asset_hw_ratio"],
        }
        keywords = {
            "gt": gt.keywords if gt else {},
            "pred": pred.keywords if pred else {},
        }
        negative_info = {
            "gt": gt.negative_assets_count if gt else 0,
            "pred": pred.negative_assets_count if pred else 0,
        }
        return cls(
            keywords=keywords,
            keywords_updated=res["new_types_added"],  # delete personal keywords cache
            cks_count=res["cks_count"],
            cks_count_total=res["cks_count_total"],
            total_assets_mbytes=res["total_assets_mbytes"],
            total_assets_count=total_assets_count,
            gt=gt,
            pred=pred,
            hist=hist,
            negative_info=negative_info,
        )


class VizDatasetStatsElement(BaseModel):
    class_ids_count: Dict[int, int]
    negative_assets_count: int


@dataclass
class DatasetStatsElement:
    keywords: Dict[str, int]
    negative_assets_count: int

    @classmethod
    def from_viz_res(cls, data: Dict, user_labels: UserLabels) -> "DatasetStatsElement":
        viz_res = VizDatasetStatsElement(**data)
        keywords = {
            user_labels.get_main_name(int(class_id)): count for class_id, count in viz_res.class_ids_count.items()
        }
        return cls(keywords, viz_res.negative_assets_count)


@dataclass
class DatasetStats:
    total_assets_count: int
    gt: DatasetStatsElement
    pred: DatasetStatsElement

    @classmethod
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "DatasetStats":
        gt = DatasetStatsElement.from_viz_res(res["gt"], user_labels)
        pred = DatasetStatsElement.from_viz_res(res["pred"], user_labels)
        return cls(total_assets_count=res["total_assets_count"], gt=gt, pred=pred)


class EvaluationScore(BaseModel):
    ap: float
    ar: float
    fn: int
    fp: int
    tp: int
    pr_curve: List[Dict]


class CKEvaluation(BaseModel):
    total: EvaluationScore
    sub: Dict[str, EvaluationScore]


class VizDatasetEvaluation(BaseModel):
    ci_evaluations: Dict[int, EvaluationScore]  # class_id -> scores
    ci_averaged_evaluation: EvaluationScore
    ck_evaluations: Dict[str, CKEvaluation]


class VizDatasetEvaluationResult(BaseModel):
    """
    Interface dataclass of VIZ output, defined as DatasetEvaluationResult in doc:
    https://github.com/IndustryEssentials/ymir/blob/master/ymir/backend/src/ymir_viz/doc/ymir_viz_API.yaml
    """

    iou_evaluations: Dict[float, VizDatasetEvaluation]  # iou -> evaluation
    iou_averaged_evaluation: VizDatasetEvaluation


class ViewerAssetRequest(BaseModel):
    """
    Payload for viewer GET /assets
    """

    class_ids: Optional[str]
    current_asset_id: Optional[str]
    cm_types: Optional[str]
    cks: Optional[str]
    tags: Optional[str]

    @validator("*", pre=True)
    def make_str(cls, v: Any) -> Optional[str]:
        if v is None:
            return v
        if isinstance(v, str):
            return v
        return ",".join(map(str, v))


class VizClient:
    def __init__(self, *, host: str = settings.VIZ_HOST):
        self.host = host
        self.session = requests.Session()
        self._user_id = None  # type: Optional[str]
        self._project_id = None  # type: Optional[str]
        self._branch_id = None  # type: Optional[str]
        self._url_prefix = None  # type: Optional[str]
        self._user_labels = None  # type: Optional[UserLabels]
        self._use_viewer = False

    def initialize(
        self,
        *,
        user_id: int,
        project_id: int,
        branch_id: Optional[str] = None,
        user_labels: Optional[UserLabels] = None,
        use_viewer: bool = False,
    ) -> None:
        self._user_id = f"{user_id:0>4}"
        self._project_id = f"{project_id:0>6}"
        if use_viewer:
            # fixme
            #  remove upon replacing all viz endpoints
            self._use_viewer = True
            host = f"127.0.0.1:{settings.VIEWER_HOST_PORT}"
            self._url_prefix = (
                f"http://{host}/api/v1/users/{self._user_id}/repo/{self._project_id}/branch"  # noqa: E501
            )
        else:
            self._url_prefix = (
                f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/branches"  # noqa: E501
            )

        if branch_id:
            self._branch_id = branch_id
        if user_labels:
            self._user_labels = user_labels

    def get_assets(
        self,
        *,
        asset_hash: Optional[str] = None,
        keyword_id: Optional[int] = None,
        keyword_ids: Optional[List[int]] = None,
        cm_types: Optional[List[str]] = None,
        cks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Assets:
        url = f"{self._url_prefix}/{self._branch_id}/assets"
        if self._use_viewer:
            payload = ViewerAssetRequest(
                class_ids=keyword_ids, cm_types=cm_types, cks=cks, tags=tags, current_asset_id=asset_hash
            ).dict(exclude_none=True)
        else:
            payload = {"class_id": keyword_id, "limit": limit, "offset": offset}

        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            logger.error("[viz] failed to get assets info: %s", resp.content)
            resp.raise_for_status()
        res = resp.json()["result"]
        logger.info("[viz] get_assets response: %s", res)
        return Assets.from_viz_res(res, self._user_labels)

    def get_asset(self, *, asset_id: str) -> Optional[Dict]:
        url = f"{self._url_prefix}/{self._branch_id}/assets/{asset_id}"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        if not resp.ok:
            logger.error("[viz] failed to get asset info: %s", resp.content)
            return None
        res = resp.json()["result"]
        return asdict(Asset.from_viz_res(asset_id, res, self._user_labels))

    def get_model(self) -> ModelMetaData:
        url = f"{self._url_prefix}/{self._branch_id}/models"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        return ModelMetaData.from_viz_res(res)

    def get_dataset(
        self, dataset_hash: Optional[str] = None, user_labels: Optional[UserLabels] = None
    ) -> DatasetMetaData:
        dataset_hash = dataset_hash or self._branch_id
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/{dataset_hash}/datasets"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viz] get_dataset response: %s", res)
        return DatasetMetaData.from_viz_res(res, user_labels)

    def get_dataset_stats(
        self, *, dataset_hash: Optional[str] = None, keyword_ids: List[int], user_labels: Optional[UserLabels] = None
    ) -> DatasetStats:
        dataset_hash = dataset_hash or self._branch_id
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/{dataset_hash}/dataset_stats"
        params = {"class_ids": ",".join(str(k) for k in keyword_ids)}
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT, params=params)
        res = self.parse_resp(resp)
        logger.info("[viz] get_dataset_stats response: %s", res)
        return DatasetStats.from_viz_res(res, user_labels)

    def get_evaluations(self) -> Dict:
        url = f"{self._url_prefix}/{self._branch_id}/evaluations"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        evaluations = {
            dataset_hash: VizDatasetEvaluationResult(**evaluation).dict() for dataset_hash, evaluation in res.items()
        }
        convert_class_id_to_keyword(evaluations, self._user_labels)
        return evaluations

    def get_fast_evaluation(
        self, dataset_hash: str, confidence_threshold: float, iou_threshold: float, need_pr_curve: bool
    ) -> Dict:
        url = f"{self._url_prefix}/{dataset_hash}/dataset_fast_evaluation"
        params = {
            "conf_thr": confidence_threshold,
            "iou_thr": iou_threshold,
            "need_pr_curve": need_pr_curve,
        }
        resp = self.session.get(url, params=params, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        evaluations = {
            dataset_hash: VizDatasetEvaluationResult(**evaluation).dict() for dataset_hash, evaluation in res.items()
        }
        convert_class_id_to_keyword(evaluations, self._user_labels)
        return evaluations

    def check_duplication(self, dataset_hashes: List[str]) -> int:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/dataset_duplication"  # noqa: E501
        params = {"candidate_dataset_ids": ",".join(dataset_hashes)}
        resp = self.session.get(url, params=params, timeout=settings.VIZ_TIMEOUT)
        return self.parse_resp(resp)

    def parse_resp(self, resp: requests.Response) -> Any:
        """
        response falls in three categories:
        1. valid result
        2. task is finished, but model not exists
        3. model not ready, try to get model later
        """
        if resp.ok:
            return resp.json()["result"]

        if resp.status_code == 400:
            logger.error("[viz] failed to parse viz response: %s", resp.content)
            error_code = resp.json()["code"]
            if error_code == VizErrorCode.MODEL_NOT_EXISTS:
                logger.error("[viz] model not found")
                raise ModelNotFound()
            elif error_code == VizErrorCode.DATASET_EVALUATION_NOT_EXISTS:
                logger.error("[viz] dataset evaluation not found")
                raise DatasetEvaluationNotFound()
            elif error_code == CMDResponseCode.RC_CMD_NO_ANNOTATIONS:
                logger.error("[viz] missing annotations for dataset evaluation")
                raise DatasetEvaluationMissingAnnotation()
        raise FailedToParseVizResponse()

    def close(self) -> None:
        self.session.close()


def get_asset_url(asset_id: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-assets/{asset_id[-2:]}/{asset_id}"


def convert_class_id_to_keyword(obj: Dict, user_labels: UserLabels) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "ci_evaluations":
                obj[key] = {user_labels.get_main_name(k): v for k, v in value.items()}
            else:
                convert_class_id_to_keyword(obj[key], user_labels)
