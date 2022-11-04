from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field, validator

from app.constants.state import MiningStrategy, IterationStage, DatasetType, ResultState


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


class IterationContext(BaseModel):
    project_id: int
    iteration_id: Optional[int]
    iteration_stage: Optional[IterationStage]
    exclude_last_result: bool = True
    mining_strategy: MiningStrategy = MiningStrategy.customize


class OperationAction(str, Enum):
    hide = "hide"
    unhide = "unhide"


class Operation(BaseModel):
    action: OperationAction = Field(example="hide")
    id_: int = Field(alias="id")


class BatchOperations(BaseModel):
    project_id: int
    operations: List[Operation]


class TypedDataset(BaseModel):
    id: int
    hash: Optional[str] = None
    type: Optional[int] = None
    exclude: bool = False
    create_datetime: Optional[datetime] = None  # type: ignore


class TypedModel(BaseModel):
    id: int
    hash: Optional[str] = None
    stage_id: Optional[int] = None
    stage_name: Optional[str] = None


class TypedLabel(BaseModel):
    name: str
    class_id: Optional[int] = None
    exclude: bool = False


def dataset_normalize(cls: Any, values: Dict) -> Dict:
    datasets = []
    if values.get("dataset_id"):
        datasets.append(TypedDataset(id=values["dataset_id"]))
    if values.get("validation_dataset_id"):
        datasets.append(TypedDataset(id=values["validation_dataset_id"], type=int(DatasetType.validation)))
    if values.get("include_datasets"):
        datasets.extend([TypedDataset(id=i) for i in values["include_datasets"]])
    if values.get("exclude_datasets"):
        datasets.extend([TypedDataset(id=i, exclude=True) for i in values["exclude_datasets"]])
    values["typed_datasets"] = datasets
    return values


def model_normalize(cls: Any, values: Dict) -> Dict:
    models = []
    if values.get("model_id"):
        models.append(TypedModel(id=values["model_id"], stage_id=values.get("model_stage_id")))
    values["typed_models"] = models
    return values


def label_normalize(cls: Any, values: Dict) -> Dict:
    labels = []
    if values.get("keywords"):
        labels.extend([TypedLabel(name=i) for i in values["keywords"]])
    if values.get("include_labels"):
        labels.extend([TypedLabel(name=i) for i in values["include_labels"]])
    if values.get("exclude_labels"):
        labels.extend([TypedLabel(name=i, exclude=True) for i in values["exclude_labels"]])
    values["typed_labels"] = labels
    return values


class MergeStrategy(IntEnum):
    stop_upon_conflict = 1
    prefer_newest = 2
    prefer_oldest = 3


class ImportStrategy(IntEnum):
    no_annotations = 1
    ignore_unknown_annotations = 2
    stop_upon_unknown_annotations = 3
    add_unknown_annotations = 4


class DatasetResult(BaseModel):
    id: int
    dataset_group_id: int
    result_state: ResultState

    class Config:
        orm_mode = True


class ModelResult(BaseModel):
    id: int
    model_group_id: int
    result_state: ResultState

    class Config:
        orm_mode = True
