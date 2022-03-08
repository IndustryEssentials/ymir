import enum
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, root_validator, validator

from app.constants.state import ResultState, TaskType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.task import TaskInternal, MergeStrategy


class ImportStrategy(enum.IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3


class DatasetBase(BaseModel):
    name: str = Field(description="Dataset Version Name")
    result_state: ResultState = ResultState.processing.value  # type: ignore
    dataset_group_id: int
    project_id: int
    # task_id haven't created yet
    # user_id can be parsed from token
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]

    class Config:
        use_enum_values = True


# Properties required for a client to create a dataset
class DatasetImport(DatasetBase):
    input_url: Optional[str] = Field(description="from url")
    input_dataset_id: Optional[int] = Field(description="from dataset of other user")
    input_path: Optional[str] = Field(description="from path on ymir server")
    strategy: ImportStrategy = Field(description="strategy about importing annotations")
    import_type: Optional[TaskType]

    @validator("import_type", pre=True, always=True)
    def gen_import_type(cls, v: TaskType, values: Any) -> TaskType:
        if values.get("input_url") or values.get("input_path"):
            from fastapi.logger import logger

            logger.warning(f"88888888888888888 {type(TaskType.import_data)}")
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
    name: Optional[str]
    result_state: Optional[ResultState]
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]


class DatasetInDBBase(
    IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, DatasetBase
):
    hash: str = Field(description="related task hash")
    version_num: int = Field(description="version num from related dataset group")
    task_id: int
    user_id: int
    related_task: Optional[TaskInternal]

    class Config:
        orm_mode = True


# Properties to return to caller
class Dataset(DatasetInDBBase):

    # make sure all the json dumped value is unpacked before returning to caller
    @root_validator(pre=True)
    def unpack_json(cls, values: Any) -> Dict:
        #       values["keywords"] = parse_optional_json(values["keywords"])
        #       values["ignored_keywords"] = parse_optional_json(values["ignored_keywords"])
        return values


class DatasetPagination(BaseModel):
    total: int
    items: List[Dataset]


class DatasetOut(Common):
    result: Dataset


class DatasetsOut(Common):
    result: List[Dataset]


class DatasetPaginationOut(Common):
    result: DatasetPagination


class DatasetsFusionParameter(BaseModel):
    dataset_group_id: int
    main_dataset_id: int
    project_id: int

    include_datasets: List[int]
    include_strategy: Optional[MergeStrategy] = Field(
        MergeStrategy.prefer_newest, description="strategy to merge multiple datasets"
    )
    exclude_datasets: List[int]

    include_labels: List[str]
    exclude_labels: List[str]

    sampling_count: int = 0
