from dataclasses import asdict, dataclass, InitVar
import json
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import ConnectionError, Timeout
from fastapi.logger import logger
from pydantic import BaseModel, dataclasses, validator, root_validator

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
class DatasetAnalysis:
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
    def from_viz_res(cls, res: Dict, user_labels: UserLabels) -> "DatasetAnalysis":
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


@dataclasses.dataclass
class DatasetStatsElement:
    keywords: Dict[str, int]
    negative_assets_count: int

    @classmethod
    def from_dict(cls, data: Dict, user_labels: UserLabels) -> "DatasetStatsElement":
        viz_res = VizDatasetStatsElement(**data)
        keywords = {
            user_labels.get_main_name(int(class_id)): count for class_id, count in viz_res.class_ids_count.items()
        }
        return cls(keywords, viz_res.negative_assets_count)


@dataclasses.dataclass
class DatasetStats:
    total_assets_count: int
    gt: DatasetStatsElement
    pred: DatasetStatsElement

    @classmethod
    def from_dict(cls, res: Dict, user_labels: UserLabels) -> "DatasetStats":
        gt = DatasetStatsElement.from_dict(res["gt"], user_labels)
        pred = DatasetStatsElement.from_dict(res["pred"], user_labels)
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


@dataclasses.dataclass
class ViewerAssetAnnotation:
    box: Dict
    class_id: int
    cm: int
    tags: Dict
    keyword: Optional[str] = None
    user_labels: InitVar[UserLabels] = None

    def __post_init__(self, user_labels: UserLabels) -> None:
        self.keyword = user_labels.get_main_name(self.class_id)


@dataclasses.dataclass
class ViewerAsset:
    asset_id: str
    class_ids: List[int]
    metadata: Dict
    gt: List
    pred: List
    cks: Dict
    url: Optional[str] = None
    hash: Optional[str] = None
    keywords: Optional[List[str]] = None
    user_labels: InitVar[UserLabels] = None

    def __post_init__(self, user_labels: UserLabels) -> None:
        self.url = get_asset_url(self.asset_id)
        self.hash = self.asset_id
        self.keywords = user_labels.get_main_names(self.class_ids)
        self.gt = [
            ViewerAssetAnnotation(i["box"], i["class_id"], i["cm"], i["tags"], user_labels=user_labels) for i in self.gt
        ]
        self.pred = [
            ViewerAssetAnnotation(i["box"], i["class_id"], i["cm"], i["tags"], user_labels=user_labels)
            for i in self.pred
        ]


@dataclasses.dataclass
class ViewerAssetsResponse:
    total_assets_count: int
    elements: List[Dict]
    total: Optional[int] = None
    items: Optional[List] = None
    user_labels: InitVar[UserLabels] = None

    def __post_init__(self, user_labels: UserLabels) -> None:
        self.total = self.total_assets_count
        self.items = [
            ViewerAsset(
                i["asset_id"],
                i["class_ids"],
                i["metadata"],
                i["gt"],
                i["pred"],
                i["cks"],
                user_labels=user_labels,
            )
            for i in self.elements
        ]

    @classmethod
    def from_dict(cls, data: Dict, user_labels: UserLabels) -> "ViewerAssetsResponse":
        return cls(data["total_assets_count"], data["elements"], user_labels=user_labels)


@dataclasses.dataclass
class ViewerDatasetAnnotation:
    class_ids_count: Dict[str, int]
    keywords: Optional[Dict[str, int]] = None
    user_labels: InitVar[UserLabels] = None

    def __post_init__(self, user_labels: UserLabels) -> None:
        self.class_ids_count = {
            user_labels.get_main_name(int(class_id)): count for class_id, count in self.class_ids_count.items()
        }


@dataclasses.dataclass
class ViewerDatasetInfoResponse:
    gt: Any
    pred: Any
    total_assets_count: int
    new_types_added: Optional[bool]
    user_labels: InitVar[UserLabels] = None

    def __post_init__(self, user_labels: UserLabels) -> None:
        self.gt = ViewerDatasetAnnotation(self.gt["class_ids_count"], user_labels=user_labels)
        self.pred = ViewerDatasetAnnotation(self.pred["class_ids_count"], user_labels=user_labels)

    @classmethod
    def from_dict(cls, data: Dict, user_labels: UserLabels) -> "ViewerDatasetInfoResponse":
        return cls(
            data["gt"], data["pred"], data["total_assets_count"], data.get("new_types_added"), user_labels=user_labels
        )


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
        use_viewer: bool = True,
    ) -> None:
        self._user_id = f"{user_id:0>4}"
        self._project_id = f"{project_id:0>6}"
        if use_viewer:
            # fixme
            #  remove upon replacing all viz endpoints
            self._use_viewer = True
            host = f"127.0.0.1:{settings.VIEWER_HOST_PORT}"
            self._url_prefix = f"http://{host}/api/v1/users/{self._user_id}/repo/{self._project_id}"  # noqa: E501
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
        """
        viewer: GET /assets
        """
        url = f"{self._url_prefix}/branch/{dataset_hash}/assets"
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

        resp = self.session.get(url, params=payload, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viz] get_assets response: %s", res)
        assets = ViewerAssetsResponse.from_dict(res, self._user_labels)
        return asdict(assets)

    def get_model_info(self) -> Dict:
        """
        viewer: GET /model_info
        """
        url = f"{self._url_prefix}/branch/{self._branch_id}/model_info"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        model_info = ViewerModelInfoResponse.parse_obj(res).dict()
        return model_info

    def get_dataset_info(self, *, dataset_hash: str, user_labels: Optional[UserLabels] = None) -> Dict:
        """
        viewer: GET /dataset_meta_count
        """
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/branch/{dataset_hash}/dataset_meta_count"
        resp = self.session.get(url, timeout=settings.VIZ_TIMEOUT)
        res = self.parse_resp(resp)
        logger.info("[viewer] dataset_meta_count response: %s", res)
        dataset_counts = ViewerDatasetInfoResponse.from_dict(res, self._user_labels)
        return asdict(dataset_counts)

    def get_dataset_analysis(
        self, dataset_hash: str, keyword_ids: Optional[List[int]] = None, require_hist: bool = False
    ) -> DatasetAnalysis:
        """
        viewer: GET /dataset_stats
        """
        url = f"{self._url_prefix}/branch/{dataset_hash}/dataset_stats"

        params = {"require_assets_hist": require_hist, "require_annos_hist": require_hist}  # type: Dict
        if keyword_ids:
            params["class_ids"] = ",".join(str(k) for k in keyword_ids)

    def get_dataset_analysis(self, dataset_hash: str) -> DatasetMetaData:
        url = f"{self._url_prefix}/{dataset_hash}/datasets"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        logger.info("[viewer] get dataset analysis response: %s", res)
        return DatasetAnalysis.from_viz_res(res, self._user_labels)

    def get_dataset_stats(
        self,
        *,
        dataset_hash: Optional[str] = None,
        keyword_ids: List[int],
        user_labels: Optional[UserLabels] = None,
    ) -> DatasetStats:
        dataset_hash = dataset_hash or self._branch_id
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/{dataset_hash}/dataset_stats"
        params = {"class_ids": ",".join(str(k) for k in keyword_ids)}
        resp = self.get_resp(url, params=params)
        res = self.parse_resp(resp)
        logger.info("[viewer] get_dataset_stats response: %s", res)
        return DatasetStats.from_dict(res, user_labels=user_labels)

    def get_fast_evaluation(
        self,
        dataset_hash: str,
        confidence_threshold: float,
        iou_threshold: float,
        need_pr_curve: bool,
    ) -> Dict:
        """
        viz: /dataset_fast_evaluation
        """
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
        convert_class_id_to_keyword(evaluations, self._user_labels)
        return evaluations

    def check_duplication(self, dataset_hashes: List[str]) -> int:
        """
        viewer: GET /dataset_duplication
        """
        url = f"{self._url_prefix}/dataset_duplication"
        params = {"candidate_dataset_ids": ",".join(dataset_hashes)}
        resp = self.get_resp(url, params=params)
        duplicated_stats = self.parse_resp(resp)
        return duplicated_stats["duplication"]

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
            logger.error("[viz] failed to parse viz error response: %s", resp.content)
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
