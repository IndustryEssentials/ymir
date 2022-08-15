from dataclasses import dataclass
import json
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import ConnectionError, Timeout
from fastapi.logger import logger
from pydantic import BaseModel, Field, validator, root_validator

from app.api.errors.errors import (
    DatasetEvaluationNotFound,
    DatasetEvaluationMissingAnnotation,
    ModelNotFound,
    FailedToParseVizResponse,
    VizError,
    VizTimeOut,
)

from app.config import settings
from common_utils.labels import UserLabels
from id_definition.error_codes import VizErrorCode, CMDResponseCode


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
    annotation_types: Optional[str]
    limit: Optional[int]
    offset: Optional[int]

    @validator("class_ids", "cm_types", "cks", "tags", "annotation_types", pre=True)
    def make_str(cls, v: Any) -> Optional[str]:
        if v is None:
            return v
        if isinstance(v, str):
            return v
        return ",".join(map(str, v))


class ViewerAssetAnnotation(BaseModel):
    box: Dict
    keyword: str
    cm: int
    tags: Dict

    @root_validator(pre=True)
    def make_up_fields(cls, values: Any) -> Any:
        values["keyword"] = values["class_id"]
        return values


class ViewerAsset(BaseModel):
    url: str
    hash: str
    keywords: List[str]
    metadata: Any
    gt: List[ViewerAssetAnnotation]
    pred: List[ViewerAssetAnnotation]
    cks: Dict

    @root_validator(pre=True)
    def make_up_fields(cls, values: Any) -> Any:
        values["url"] = get_asset_url(values["asset_id"])
        values["hash"] = values["asset_id"]
        values["keywords"] = values["class_ids"]
        return values


class ViewerAssetsResponse(BaseModel):
    items: List[ViewerAsset]
    total: int

    @root_validator(pre=True)
    def make_up_fields(cls, values: Any) -> Any:
        values["items"] = values["elements"]
        values["total"] = values.get("total_assets_count", 0)
        return values


class ViewerDatasetAnnotation(BaseModel):
    class_ids_count: Dict[int, int]


class ViewerDatasetInfoResponse(BaseModel):
    gt: ViewerDatasetAnnotation
    pred: ViewerDatasetAnnotation
    total_assets_count: int
    new_types_added: Optional[bool] = Field(description="delete keywords cache if having new_types_added")


class ViewerModelInfoResponse(BaseModel):
    hash: str
    map: float
    task_parameters: str
    executor_config: Dict
    model_stages: Dict
    best_stage_name: str
    keywords: Optional[str]

    @root_validator(pre=True)
    def make_up_fields(cls, values: Any) -> Any:
        keywords = values["executor_config"].get("class_names")
        values.update(
            hash=values["model_id"],
            map=values["model_mAP"],
            keywords=json.dumps(keywords) if keywords else None,
        )
        return values


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
        dataset_hash: str,
        asset_hash: Optional[str] = None,
        keyword_id: Optional[int] = None,
        keyword_ids: Optional[List[int]] = None,
        cm_types: Optional[List[str]] = None,
        cks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        annotation_types: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Dict:
        url = f"{self._url_prefix}/{dataset_hash}/assets"
        if self._use_viewer:
            payload = ViewerAssetRequest(
                class_ids=keyword_ids,
                cm_types=cm_types,
                cks=cks,
                tags=tags,
                annotation_types=annotation_types,
                current_asset_id=asset_hash,
                limit=limit,
                offset=offset,
            ).dict(exclude_none=True)
        else:
            payload = {"class_id": keyword_id, "limit": limit, "offset": offset}

        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viz] get_assets response: %s", res)
        convert_class_id_to_keyword(res, self._user_labels, ["class_id", "class_ids"])
        logger.info("[viz] replace class_ids with keywords")
        assets = ViewerAssetsResponse.parse_obj(res).dict()
        return assets

    def get_model_info(self) -> Dict:
        url = f"{self._url_prefix}/{self._branch_id}/models"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        model_info = ViewerModelInfoResponse.parse_obj(res).dict()
        return model_info

    def get_dataset_info(self, *, dataset_hash: str, user_labels: Optional[UserLabels] = None) -> Dict:
        """
        viewer: GET dataset_meta_count
        """
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/{dataset_hash}/dataset_meta_count"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viz] dataset_meta_count response: %s", res)
        dataset_counts = ViewerDatasetInfoResponse.parse_obj(res).dict()
        convert_class_id_to_keyword(dataset_counts, self._user_labels, ["class_ids_count"])
        return dataset_counts

    def get_dataset_analysis(self, dataset_hash: str) -> DatasetMetaData:
        url = f"{self._url_prefix}/{dataset_hash}/datasets"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        logger.info("[viz] get dataset analysis response: %s", res)
        return DatasetMetaData.from_viz_res(res, self._user_labels)

    def get_dataset_stats(
        self, *, dataset_hash: Optional[str] = None, keyword_ids: List[int], user_labels: Optional[UserLabels] = None
    ) -> DatasetStats:
        dataset_hash = dataset_hash or self._branch_id
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/{dataset_hash}/dataset_stats"
        params = {"class_ids": ",".join(str(k) for k in keyword_ids)}
        resp = self.get_resp(url, params=params)
        res = self.parse_resp(resp)
        logger.info("[viz] get_dataset_stats response: %s", res)
        return DatasetStats.from_viz_res(res, user_labels)

    def get_fast_evaluation(
        self, dataset_hash: str, confidence_threshold: float, iou_threshold: float, need_pr_curve: bool
    ) -> Dict:
        url = f"{self._url_prefix}/{dataset_hash}/dataset_fast_evaluation"
        params = {
            "conf_thr": confidence_threshold,
            "iou_thr": iou_threshold,
            "need_pr_curve": need_pr_curve,
        }
        resp = self.get_resp(url, params=params)
        res = self.parse_resp(resp)
        evaluations = {
            dataset_hash: VizDatasetEvaluationResult(**evaluation).dict() for dataset_hash, evaluation in res.items()
        }
        convert_class_id_to_keyword(evaluations, self._user_labels, ["ci_evaluations"])
        return evaluations

    def check_duplication(self, dataset_hashes: List[str]) -> int:
        url = f"http://{self.host}/v1/users/{self._user_id}/repositories/{self._project_id}/dataset_duplication"  # noqa: E501
        params = {"candidate_dataset_ids": ",".join(dataset_hashes)}
        resp = self.get_resp(url, params=params)
        return self.parse_resp(resp)

    def get_resp(
        self, url: str, params: Optional[Dict] = None, timeout: int = settings.VIZ_TIMEOUT
    ) -> requests.Response:
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
        except ConnectionError:
            raise VizError()
        except Timeout:
            raise VizTimeOut()
        else:
            return resp

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


def convert_class_id_to_keyword(obj: Dict, user_labels: UserLabels, targets: List[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in targets:
                if isinstance(value, dict):
                    obj[key] = {user_labels.get_main_name(k): v for k, v in value.items()}
                elif isinstance(value, list):
                    obj[key] = [k for k in user_labels.get_main_names(value) if k is not None]
                else:
                    obj[key] = user_labels.get_main_name(value)
            else:
                convert_class_id_to_keyword(obj[key], user_labels, targets)
    elif isinstance(obj, list):
        for item in obj:
            convert_class_id_to_keyword(item, user_labels, targets)
