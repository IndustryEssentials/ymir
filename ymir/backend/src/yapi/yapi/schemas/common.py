from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
import uuid

from pydantic import BaseModel, Field, validator, root_validator

from yapi.config import settings


def generate_uuid() -> str:
    return str(uuid.uuid4())


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
    def AdaptAppResponse(cls, values: Any) -> Any:
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
