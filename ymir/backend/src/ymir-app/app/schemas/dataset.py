import enum
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, root_validator

from app.constants.state import ResultState
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.task import TaskInternal


class ImportStrategy(enum.IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3


class DatasetBase(BaseModel):
    name: str = Field(description="Dataset Version Name")
    version_num: int
    result_state: ResultState = ResultState.processing
    dataset_group_id: int
    project_id: int
    # task_id haven't created yet
    # user_id can be parsed from token
    keywords: Optional[str]
    ignored_keywords: Optional[str]
    asset_count: Optional[int]
    keyword_count: Optional[int]


class DatasetImport(DatasetBase):
    input_url: Optional[str] = Field(description="from url")
    input_dataset_id: Optional[int] = Field(description="from dataset of other user")
    input_token: Optional[str] = Field(description="from uploaded file token")
    input_path: Optional[str] = Field(description="from path on ymir server")
    strategy: ImportStrategy = Field(description="strategy about importing annotations")

    @root_validator
    def check_input_source(cls, values: Any) -> Any:
        fields = ("input_url", "input_dataset_id", "input_token", "input_path")
        if all(values.get(i) is None for i in fields):
            raise ValueError("Missing input source")
        return values


# Sufficient properties to create a dataset
class DatasetCreate(DatasetBase):
    hash: str = Field(description="related task hash")
    task_id: int
    user_id: int


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
