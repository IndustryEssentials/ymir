from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, root_validator
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    Annotation,
    AnnotationStats,
)


class PredictionBase(BaseModel):
    pass


class Prediction(IdModelMixin, DateTimeModelMixin, PredictionBase):
    object_type: int
    dataset_version_id: int
    model_version_id: int
    task_id: int
    source: int
    asset_count: Optional[int]
    class_name_count: Optional[int]
    class_names: List[str]
    evaluation_state: Optional[int]

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["dataset_version_id"] = values["dataset_id"]
        values["model_version_id"] = values["model_id"]
        try:
            values["class_names"] = list(values["keywords"]["pred"].keys())
        except KeyError:
            values["class_names"] = []
        values["class_name_count"] = values.get("keyword_count") or len(
            values["class_names"]
        )
        return values


class PredictionPagination(BaseModel):
    total: int
    items: Dict[int, List[Prediction]]  # model_version_id -> List[Prediction]


class PredictionPaginationOut(Common):
    result: PredictionPagination


class PredictionWithAnnotation(Prediction):
    gt_stats: Optional[AnnotationStats]
    pred_stats: Optional[AnnotationStats]

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["gt_stats"] = values.get("gt")
        values["pred_stats"] = values.get("pred")
        values["dataset_version_id"] = values["dataset_id"]
        values["model_version_id"] = values["model_id"]
        try:
            values["class_names"] = list(values["keywords"]["pred"].keys())
        except KeyError:
            values["class_names"] = []
        values["class_name_count"] = values.get("keyword_count") or len(
            values["class_names"]
        )
        return values


class PredictionOut(Common):
    result: PredictionWithAnnotation


#   result: Dict


class PredictionAsset(BaseModel):
    hash: str = Field(description="DocId")
    url: str
    metadata: Optional[Dict]
    class_names: Optional[List[str]]
    gt: Optional[List[Annotation]]
    pred: Optional[List[Annotation]]

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        values["class_names"] = values.get("keywords")
        return values


class PredictionAssetPagination(BaseModel):
    total: int
    items: List[PredictionAsset]


class PredictionAssetPaginationOut(Common):
    result: PredictionAssetPagination


class PredictionEvaluationOut(Common):
    result: Dict

    @root_validator(pre=True)
    def AdaptAppResponse(cls, values: Any) -> Any:
        for _, result in values.get("result", {}).items():
            values["result"] = result
        return values
