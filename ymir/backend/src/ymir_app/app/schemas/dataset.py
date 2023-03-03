import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from app.constants.state import ResultState, TaskType, ObjectType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
    ImportStrategy,
)
from app.schemas.task import TaskInternal


class DatasetBase(BaseModel):
    source: TaskType
    description: Optional[str]
    result_state: ResultState = ResultState.processing
    dataset_group_id: int
    project_id: int
    # task_id haven't created yet
    # user_id can be parsed from token
    keywords: Optional[str]
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
    object_type: Optional[ObjectType] = ObjectType.object_detect
    is_visible: bool

    class Config:
        orm_mode = True


class DatasetInDB(DatasetInDBBase):
    pass


# Properties to return to caller
class Dataset(DatasetInDBBase):
    keywords: Optional[str]

    # make sure all the json dumped value is unpacked before returning to caller
    @validator("keywords")
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


class DatasetAnnotationHist(BaseModel):
    quality: List[Dict] = []
    box_area: List[Dict] = []
    box_area_ratio: List[Dict] = []
    class_counts: List[Dict] = []
    # instance segmentation
    mask_area: List[Dict] = []
    obj_counts: List[Dict] = []  # crowdedness


class DatasetAnnotation(BaseModel):
    keywords: Dict[str, int]
    negative_assets_count: int
    tags_count_total: Dict  # box tags in first level
    tags_count: Dict  # box tags in second level

    hist: Optional[DatasetAnnotationHist]
    annos_count: Optional[int]
    ave_annos_count: Optional[float]

    eval_class_ids: Optional[List]

    # segmentation
    classwise_area: Optional[Dict]
    # instance segmentation
    classwise_annos_count: Optional[Dict]
    # semantic segmentation
    total_mask_area: Optional[int]


class DatasetInfo(DatasetInDBBase):
    gt: Optional[DatasetAnnotation]
    pred: Optional[DatasetAnnotation]

    keywords: Optional[Any]
    cks_count: Optional[Dict]
    cks_count_total: Optional[Dict]

    total_assets_count: Optional[int]
    evaluation_state: Optional[int]

    # make sure all the json dumped value is unpacked before returning to caller
    @validator("keywords")
    def unpack(cls, v: Optional[Union[str, Dict]]) -> Dict[str, int]:
        if v is None:
            return {}
        if isinstance(v, str):
            return json.loads(v)
        return v


class DatasetInfoOut(Common):
    result: DatasetInfo


class DatasetHist(BaseModel):
    bytes: List[Dict]
    area: List[Dict]
    quality: List[Dict]
    hw_ratio: List[Dict]


class DatasetAnalysis(DatasetInfo):
    total_assets_mbytes: Optional[int]
    hist: Optional[DatasetHist]


class DatasetsAnalysesOut(Common):
    result: List[DatasetAnalysis]


class DatasetPaginationOut(Common):
    result: DatasetPagination


class MultiDatasetsWithProjectID(BaseModel):
    project_id: int
    dataset_ids: List[int]


class DatasetCheckDuplicationOut(Common):
    result: int
