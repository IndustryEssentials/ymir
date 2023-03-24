from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, root_validator
from yapi.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    Annotation,
    AnnotationStats,
)


class DatasetBase(BaseModel):
    name: str = Field(description="Dataset Name")
    project_id: int
    user_id: int
    description: Optional[str]


class Dataset(IdModelMixin, DateTimeModelMixin, DatasetBase):
    pass


class DatasetPagination(BaseModel):
    total: int
    items: List[Dataset]


class DatasetPaginationOut(Common):
    result: DatasetPagination


class DatasetOut(Common):
    result: Dataset


class DatasetVersionBase(BaseModel):
    pass


class DatasetVersion(DatasetVersionBase, IdModelMixin, DateTimeModelMixin):
    task_id: int
    result_state: int
    object_type: int
    class_names: List[str] = []
    asset_count: Optional[int]
    class_name_count: Optional[int]
    gt_stats: Optional[AnnotationStats]

    @root_validator(pre=True)
    def AdapteAppResponse(cls, values: Any) -> Any:
        if values.get("keywords"):
            values["class_names"] = list(values["keywords"].keys())
        values["class_name_count"] = values["keyword_count"]
        values["gt_stats"] = values.get("gt")
        return values


class DatasetVersionOut(Common):
    result: DatasetVersion


class DatasetVersionPagination(BaseModel):
    total: int
    items: List[DatasetVersion]


class DatasetVersionPaginationOut(Common):
    result: DatasetVersionPagination


class DatasetAsset(BaseModel):
    hash: str = Field(description="DocId")
    url: str
    metadata: Optional[Dict]
    class_names: Optional[List[str]]
    gt: Optional[List[Annotation]]

    @root_validator(pre=True)
    def AdapteAppResponse(cls, values: Any) -> Any:
        values["class_names"] = values.get("keywords")
        return values


class DatasetAssetPagination(BaseModel):
    total: int
    items: List[DatasetAsset]


class DatasetAssetPaginationOut(Common):
    result: DatasetAssetPagination
