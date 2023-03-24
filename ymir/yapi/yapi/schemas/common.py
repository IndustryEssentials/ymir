from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field, validator, root_validator

from yapi.config import settings


class Common(BaseModel):
    code: int = 0
    message: str = "success"


class DateTimeModelMixin(BaseModel):
    create_datetime: datetime = None  # type: ignore
    update_datetime: datetime = None  # type: ignore

    @validator("create_datetime", "update_datetime", pre=True)
    def default_datetime(
        cls,
        value: datetime,
    ) -> datetime:  # noqa: N805  # noqa: WPS110
        return value or datetime.now()


class IdModelMixin(BaseModel):
    id: int = Field(alias="id")


class IsDeletedModelMixin(BaseModel):
    is_deleted: bool = False


class OperationAction(str, Enum):
    hide = "hide"
    unhide = "unhide"


class Operation(BaseModel):
    action: OperationAction = Field(example="hide")
    id_: int = Field(alias="id")


class BatchOperations(BaseModel):
    project_id: int
    operations: List[Operation]


class MergeStrategy(IntEnum):
    stop_upon_conflict = 1
    prefer_newest = 2
    prefer_oldest = 3


class ImportStrategy(IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3
    add_unknown_annotations = 4


# Common Query Parameters


class SortField(Enum):
    id = "id"
    create_datetime = "create_datetime"
    update_datetime = "update_datetime"
    asset_count = "asset_count"
    source = "source"
    map = "map"  # Model
    duration = "duration"  # Task


class CommonPaginationParams(BaseModel):
    offset: int = 0
    limit: Optional[int] = settings.DEFAULT_LIMIT
    order_by: SortField = SortField.id
    is_desc: bool = True
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class Annotation(BaseModel):
    box: Optional[Dict]
    mask: Optional[str]
    polygon: Optional[List[Dict]]
    class_name: Optional[str]
    score: Optional[float]

    @root_validator(pre=True)
    def AdapteAppResponse(cls, values: Any) -> Any:
        values["class_name"] = values.get("keyword")
        return values


class AnnotationStats(BaseModel):
    annos_count: Optional[int]
    classwise_assets_count: Optional[Dict]
    classwise_area: Optional[Dict]
    classwise_annos_count: Optional[Dict]
    total_mask_area: Optional[int]


class AssetTimeStamp(BaseModel):
    start: int
    duration: int


class AssetMetadata(BaseModel):
    timestamp: Optional[AssetTimeStamp]
    tvt_type: Optional[int]
    asset_type: Optional[int]
    width: Optional[int]
    height: Optional[int]
    image_channels: Optional[int]
    byte_size: Optional[int]
    origin_filename: Optional[str]
