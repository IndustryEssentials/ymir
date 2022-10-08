import enum
import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator, root_validator

from app.constants.state import LabelType, ResultState, TaskType
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
    add_unknown_annotations = 4


class MergeStrategy(enum.IntEnum):
    stop_upon_conflict = 1
    prefer_newest = 2
    prefer_oldest = 3


class DatasetBase(BaseModel):
    source: TaskType
    description: Optional[str]
    label_type: LabelType = LabelType.object_detect
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
    label_type: LabelType = LabelType.object_detect
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
    description: Optional[str]

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
    quality: List[Dict]
    area: List[Dict]
    area_ratio: List[Dict]


class DatasetAnnotation(BaseModel):
    keywords: Dict[str, int]
    negative_assets_count: int
    tags_count_total: Dict  # box tags in first level
    tags_count: Dict  # box tags in second level

    hist: Optional[DatasetAnnotationHist]
    annos_count: Optional[int]
    ave_annos_count: Optional[float]

    eval_class_ids: Optional[List]


class DatasetInfo(DatasetInDBBase):
    gt: Optional[DatasetAnnotation]
    pred: Optional[DatasetAnnotation]

    keywords: Optional[Any]
    cks_count: Optional[Dict]
    cks_count_total: Optional[Dict]

    total_assets_count: Optional[int]

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

    description: Optional[str] = Field(description="description for fusion result")


class DatasetEvaluationCreate(BaseModel):
    project_id: int
    dataset_ids: List[int]
    confidence_threshold: float
    iou_threshold: float
    require_average_iou: bool = False
    need_pr_curve: bool = True
    main_ck: Optional[str] = None


class DatasetEvaluationOut(Common):
    # dict of dataset_id to evaluation result
    result: Dict[int, Dict]


class MultiDatasetsWithProjectID(BaseModel):
    project_id: int
    dataset_ids: List[int]


class DatasetCheckDuplicationOut(Common):
    result: int


class DatasetMergeCreate(BaseModel):
    project_id: int
    dest_group_id: Optional[int]
    dest_group_name: Optional[str]
    include_datasets: List[int]
    exclude_datasets: Optional[List[int]]
    merge_strategy: MergeStrategy = Field(
        MergeStrategy.prefer_newest, description="strategy to merge multiple datasets"
    )
    description: Optional[str] = Field(description="description for merge result")

    @root_validator
    def confine_parameters(cls, values: Any) -> Any:
        if values.get("dest_group_id") is None and values.get("dest_group_name") is None:
            raise ValueError("dest_group_id and dest_group_name cannot both be None")
        return values


class DatasetFilterCreate(BaseModel):
    project_id: int
    dataset_id: int
    include_keywords: Optional[List[str]]
    exclude_keywords: Optional[List[str]]
    sampling_count: Optional[int]
    description: Optional[str] = Field(description="description for filter result")

    @root_validator
    def confine_parameters(cls, values: Any) -> Any:
        if (
            values.get("include_keywords") is None
            and values.get("exclude_keywords") is None
            and values.get("sampling_count") is None
        ):
            raise ValueError("include_keywords, exclude_keywords and sampling_count cannot all be None")
        return values
