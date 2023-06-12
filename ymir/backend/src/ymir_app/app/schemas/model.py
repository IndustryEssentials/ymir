import os
from typing import Any, Callable, Dict, List, Optional
import json

from pydantic import BaseModel, Field, root_validator, validator

from app.api.errors.errors import ModelNotFound, TaskNotFound, FieldValidationFailed
from app.config import settings
from app.constants.state import ResultState, TaskType, ObjectType
from app.schemas.common import (
    Common,
    DateTimeModelMixin,
    IdModelMixin,
    IsDeletedModelMixin,
)
from app.schemas.model_stage import ModelStageInDBBase
from app.schemas.task import TaskInternal
from app.utils.files import NGINX_DATA_PATH
from id_definition.task_id import gen_repo_hash, gen_user_hash


def get_model_url(model_hash: str) -> str:
    return f"{settings.NGINX_PREFIX}/ymir-models/{model_hash}"


class ModelBase(BaseModel):
    hash: Optional[str] = None
    source: TaskType
    description: Optional[str]
    map: Optional[float] = Field(description="Mean Average Precision")
    miou: Optional[float] = Field(description="Mean IoU")
    mask_ap: Optional[float] = Field(description="Mask Average Precision")
    keywords: Optional[str]
    result_state: ResultState = ResultState.processing
    model_group_id: int
    project_id: int
    task_id: Optional[int]
    user_id: Optional[int]


class ModelImport(BaseModel):
    project_id: int
    group_name: str = Field(description="Model Group Name")
    description: Optional[str]
    input_model_path: Optional[str] = Field(description="from uploaded file url")
    input_model_id: Optional[int] = Field(description="from model of other user")
    input_url: Optional[str] = Field(description="model url")
    source: Optional[TaskType]
    import_type: Optional[TaskType]

    @validator("import_type", "source", pre=True, always=True)
    def gen_import_type(cls, v: TaskType, values: Any) -> TaskType:
        if values.get("input_model_id"):
            return TaskType.copy_model
        elif values.get("input_model_path") or values.get("input_url"):
            return TaskType.import_model
        else:
            raise ValueError("Missing input source")

    def get_import_parameters(self, model_getter: Callable) -> Dict[str, Any]:
        if self.import_type == TaskType.copy_model:
            source_model = model_getter(self.input_model_id)
            if source_model is None:
                raise ModelNotFound()
            if source_model.related_task is None:
                raise TaskNotFound()
            return {
                "src_user_id": gen_user_hash(source_model.user_id),
                "src_repo_id": gen_repo_hash(source_model.project_id),
                "src_resource_id": source_model.related_task.hash,
            }
        elif self.import_type == TaskType.import_model:
            if self.input_model_path is not None:
                return {"model_package_path": os.path.join(NGINX_DATA_PATH, self.input_model_path)}
            elif self.input_url:
                return {"model_package_path": self.input_url}
        else:
            raise FieldValidationFailed()


class ModelCreate(ModelBase):
    task_id: int
    user_id: int
    description: Optional[str]


class ModelUpdate(BaseModel):
    description: Optional[str]
    recommended_stage: Optional[int] = Field(alias="stage_id")


class ModelInDBBase(IdModelMixin, DateTimeModelMixin, IsDeletedModelMixin, ModelBase):
    name: str
    group_name: str
    version_num: int
    related_task: Optional[TaskInternal]
    is_visible: bool
    related_stages: List[ModelStageInDBBase]
    recommended_stage: Optional[int] = None
    object_type: Optional[ObjectType] = ObjectType.object_detect

    class Config:
        orm_mode = True


# Properties to return to caller
class Model(ModelInDBBase):
    keywords: Optional[str]
    url: Optional[str] = None

    @root_validator
    def make_up_url(cls, values: Any) -> Any:
        # make up the model url
        if values.get("hash"):
            values["url"] = get_model_url(values["hash"])
        return values

    # unpack json dumpped keywords before returning to caller
    @validator("keywords")
    def unpack(cls, v: Optional[str]) -> List[str]:
        if v is None:
            return []
        return json.loads(v)


class ModelPagination(BaseModel):
    total: int
    items: List[Model]


class ModelOut(Common):
    result: Model


class ModelsOut(Common):
    result: List[Model]


class ModelPaginationOut(Common):
    result: ModelPagination


class StageChange(BaseModel):
    stage_id: int
