import enum
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.constants.state import ResultState, TaskType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
    RequestParameterBase,
)
from app.schemas.task import TaskInternal


class ImportStrategy(enum.IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3


class MergeStrategy(enum.IntEnum):
    stop_upon_conflict = 1
    prefer_newest = 2
    prefer_oldest = 3


class DatasetBase(BaseModel):
    source: TaskType
    description: Optional[str]
    result_state: ResultState = ResultState.processing
    dataset_group_id: int
    project_id: int
    # task_id haven't created yet
    # user_id can be parsed from token
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    negative_info: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]

    class Config:
        use_enum_values = True
        validate_all = True


# Properties required for a client to create a dataset
class DatasetImport(BaseModel):
    group_name: str = Field(description="Dataset Group Name")
    description: Optional[str]
    project_id: int
    input_url: Optional[str] = Field(description="from url")
    input_dataset_id: Optional[int] = Field(description="from dataset of other user")
    input_dataset_name: Optional[str] = Field(description="name for source dataset")
    input_path: Optional[str] = Field(description="from path on ymir server")
    strategy: ImportStrategy = ImportStrategy.ignore_unknown_annotations
    source: Optional[TaskType]
    import_type: Optional[TaskType]

    @validator("import_type", "source", pre=True, always=True)
    def gen_import_type(cls, v: TaskType, values: Any) -> TaskType:
        if values.get("input_url") or values.get("input_path"):
            return TaskType.import_data
        elif values.get("input_dataset_id"):
            return TaskType.copy_data
        else:
            raise ValueError("Missing input source")


# Sufficient properties to create a dataset
class DatasetCreate(DatasetBase):
    hash: str = Field(description="related task hash")
    task_id: int
    user_id: int

    class Config:
        use_enum_values = True


# Properties that can be changed
class DatasetUpdate(BaseModel):
    description: Optional[str]
    result_state: Optional[ResultState]
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    negative_info: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]


class DatasetInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DatasetBase):
    name: str
    group_name: str
    hash: str = Field(description="related task hash")
    version_num: int = Field(description="version num from related dataset group")
    task_id: int
    user_id: int
    related_task: Optional[TaskInternal]

    class Config:
        orm_mode = True


# Properties to return to caller
class Dataset(DatasetInDBBase):
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    negative_info: Optional[str]

    # make sure all the json dumped value is unpacked before returning to caller
    @validator("keywords", "ignored_keywords", "negative_info")
    def unpack(cls, v: Optional[str]) -> Dict[str, int]:
        if v is None:
            return {}
        return json.loads(v)

    class Config:
        use_enum_values = True
        validate_all = True


class DatasetPagination(BaseModel):
    total: int
    items: List[Dataset]


class DatasetOut(Common):
    result: Dataset


class DatasetsOut(Common):
    result: List[Dataset]


class DatasetPaginationOut(Common):
    result: DatasetPagination


class DatasetsFusionParameter(RequestParameterBase):
    dataset_group_id: int
    main_dataset_id: int

    include_datasets: List[int]
    include_strategy: Optional[MergeStrategy] = Field(
        MergeStrategy.prefer_newest, description="strategy to merge multiple datasets"
    )
    exclude_datasets: List[int]

    include_labels: List[str]
    exclude_labels: List[str]

    sampling_count: int = 0
