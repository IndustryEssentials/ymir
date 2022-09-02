from dataclasses import asdict, InitVar
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


@dataclasses.dataclass
class DatasetAnnotation:
    keywords: Dict[str, int]
    class_ids_count: Dict[str, int]
    negative_assets_count: int

    tags_count_total: Dict
    tags_count: Dict

    hist: Optional[Dict]
    annos_count: Optional[int]
    ave_annos_count: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict, total_assets_count: int, user_labels: UserLabels) -> "DatasetAnnotation":
        ave_annos_count = round(data["annos_count"] / total_assets_count, 2) if total_assets_count else None
        keywords = {
            user_labels.get_main_name(int(class_id)): count for class_id, count in data["class_ids_count"].items()
        }
        return cls(
            keywords=keywords,
            class_ids_count=data["class_ids_count"],
            negative_assets_count=data["negative_assets_count"],
            tags_count_total=data["tags_count_total"],
            tags_count=data["tags_count"],
            hist=data.get("annos_hist") or None,
            annos_count=data.get("annos_count"),
            ave_annos_count=ave_annos_count,
        )


@dataclasses.dataclass
class DatasetInfo:
    gt: Optional[DatasetAnnotation]
    pred: Optional[DatasetAnnotation]

    cks_count: Dict
    cks_count_total: Dict

    keywords: Dict
    new_types_added: Optional[bool]

    total_assets_count: int

    hist: Optional[Dict] = None
    total_assets_mbytes: Optional[int] = None

    @classmethod
    def from_dict(cls, res: Dict, user_labels: UserLabels) -> "DatasetInfo":
        total_assets_count = res["total_assets_count"]
        gt = DatasetAnnotation.from_dict(res["gt"], total_assets_count, user_labels) if res.get("gt") else None
        pred = DatasetAnnotation.from_dict(res["pred"], total_assets_count, user_labels) if res.get("pred") else None
        keywords = {
            "gt": gt.keywords if gt else {},
            "pred": pred.keywords if pred else {},
        }
        return cls(
            gt=gt,
            pred=pred,
            cks_count=res["cks_count"],
            cks_count_total=res["cks_count_total"],
            keywords=keywords,
            new_types_added=res.get("new_types_added"),
            total_assets_count=total_assets_count,
            hist=res.get("assets_hist") or None,
            total_assets_mbytes=res.get("total_assets_mbytes"),
        )


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
            ViewerAssetAnnotation(
                box=i["box"],
                class_id=i["class_id"],
                cm=i["cm"],
                tags=i["tags"],
                user_labels=user_labels,
            )
            for i in self.gt
        ]
        self.pred = [
            ViewerAssetAnnotation(
                box=i["box"],
                class_id=i["class_id"],
                cm=i["cm"],
                tags=i["tags"],
                user_labels=user_labels,
            )
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
                asset_id=i["asset_id"],
                class_ids=i["class_ids"],
                metadata=i["metadata"],
                gt=i["gt"],
                pred=i["pred"],
                cks=i["cks"],
                user_labels=user_labels,
            )
            for i in self.elements
        ]

    @classmethod
    def from_dict(cls, data: Dict, user_labels: UserLabels) -> "ViewerAssetsResponse":
        return cls(data["total_assets_count"], data["elements"], user_labels=user_labels)


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
            hash=values["model_hash"],
            map=values["mean_average_precision"],
            model_stages=values["stages"],
            keywords=json.dumps(keywords) if keywords else None,
        )
        return values


class VizClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self._user_id = None  # type: Optional[str]
        self._project_id = None  # type: Optional[str]
        self._branch_id = None  # type: Optional[str]
        self._host = f"http://127.0.0.1:{settings.VIEWER_HOST_PORT}"
        self._url_prefix = None  # type: Optional[str]
        self._user_labels = None  # type: Optional[UserLabels]

    def initialize(
        self,
        *,
        user_id: int,
        project_id: int,
        user_labels: Optional[UserLabels] = None,
    ) -> None:
        self._user_id = f"{user_id:0>4}"
        self._project_id = f"{project_id:0>6}"
        self._url_prefix = f"{self._host}/api/v1/users/{self._user_id}/repo/{self._project_id}"  # noqa: E501

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
        params = ViewerAssetRequest(
            class_ids=keyword_ids,
            cm_types=cm_types,
            cks=cks,
            tags=tags,
            annotation_types=annotation_types,
            current_asset_id=asset_hash,
            limit=limit,
            offset=offset,
        ).dict(exclude_none=True)

        resp = self.get_resp(url, params=params)
        res = self.parse_resp(resp)
        assets = ViewerAssetsResponse.from_dict(res, self._user_labels)
        return asdict(assets)

    def get_model_info(self, branch_id: str) -> Dict:
        """
        viewer: GET /model_info
        """
        url = f"{self._url_prefix}/branch/{branch_id}/model_info"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        model_info = ViewerModelInfoResponse.parse_obj(res).dict()
        return model_info

    def get_dataset_info(self, dataset_hash: str, user_labels: Optional[UserLabels] = None) -> Dict:
        """
        viewer: GET /dataset_meta_count
        """
        user_labels = user_labels or self._user_labels
        url = f"{self._url_prefix}/branch/{dataset_hash}/dataset_meta_count"
        resp = self.get_resp(url)
        res = self.parse_resp(resp)
        dataset_info = DatasetInfo.from_dict(res, user_labels=user_labels)
        return asdict(dataset_info)

    def get_dataset_analysis(
        self,
        dataset_hash: str,
        keyword_ids: Optional[List[int]] = None,
        require_hist: bool = False,
    ) -> Dict:
        """
        viewer: GET /dataset_stats
        """
        url = f"{self._url_prefix}/branch/{dataset_hash}/dataset_stats"

        params = {
            "require_assets_hist": require_hist,
            "require_annos_hist": require_hist,
        }  # type: Dict
        if keyword_ids:
            params["class_ids"] = ",".join(str(k) for k in keyword_ids)

        resp = self.get_resp(url, params=params)
        res = self.parse_resp(resp)
        dataset_info = DatasetInfo.from_dict(res, self._user_labels)
        return asdict(dataset_info)

    def check_duplication(self, dataset_hashes: List[str]) -> int:
        """
        viewer: GET /dataset_duplication
        """
        url = f"{self._url_prefix}/dataset_duplication"
        params = {"candidate_dataset_ids": ",".join(dataset_hashes)}
        resp = self.get_resp(url, params=params)
        duplicated_stats = self.parse_resp(resp)
        return duplicated_stats["duplication"]

    def send_metrics(
        self,
        metrics_group: str,
        id: str,
        create_time: int,
        keyword_ids: List[int],
        extra_data: Optional[Dict] = None,
    ) -> None:
        url = f"{self._host}/api/v1/user_metrics/{metrics_group}"
        payload = extra_data or {}
        payload.update(
            {
                "id": id,
                "create_time": create_time,
                "user_id": self._user_id,
                "project_id": self._project_id,
                "class_ids": ",".join(map(str, keyword_ids)),
            }
        )
        self.post(url, payload)

    def query_metrics(
        self,
        metrics_group: str,
        user_id: int,
        query_field: str,
        bucket: str,
        unit: str = "",
        limit: int = 10,
        keyword_ids: Optional[List[int]] = None,
    ) -> Dict:
        url = f"{self._host}/api/v1/user_metrics/{metrics_group}"
        params = {
            "user_id": f"{user_id:0>4}",
            "query_field": query_field,
            "bucket": bucket,
            "unit": unit,
            "limit": limit,
        }
        if keyword_ids:
            params["class_ids"] = ",".join(map(str, keyword_ids))
        resp = self.get_resp(url, params=params)
        return self.parse_resp(resp)

    def post(self, url: str, payload: Optional[Dict], timeout: int = settings.VIZ_TIMEOUT) -> requests.Response:
        logger.info("[viewer] request url %s and payload %s", url, payload)
        try:
            resp = self.session.post(url, data=payload, timeout=timeout)
        except ConnectionError:
            raise VizError()
        except Timeout:
            raise VizTimeOut()
        else:
            return resp

    def get_resp(
        self,
        url: str,
        params: Optional[Dict] = None,
        timeout: int = settings.VIZ_TIMEOUT,
    ) -> requests.Response:
        logger.info("[viewer] request url %s and params %s", url, params)
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
            res = resp.json()["result"]
            logger.info("[viewer] successful response: %s", res)
            return res

        logger.error("[viewer] error response: %s", resp.content)
        if resp.status_code == 400:
            error_code = resp.json()["code"]
            if error_code == VizErrorCode.MODEL_NOT_EXISTS:
                logger.error("[viewer] model not found")
                raise ModelNotFound()
            elif error_code == VizErrorCode.DATASET_EVALUATION_NOT_EXISTS:
                logger.error("[viewer] dataset evaluation not found")
                raise DatasetEvaluationNotFound()
            elif error_code == CMDResponseCode.RC_CMD_NO_ANNOTATIONS:
                logger.error("[viewer] missing annotations for dataset evaluation")
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
