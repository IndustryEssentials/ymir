from collections import Counter
from pathlib import Path
from typing import List

from loguru import logger
from pydantic import BaseModel, Field, validator

from conf.configs import conf
from utils.constants import DataSetResultTypes, FiftyoneTaskStatus
from utils.errors import FiftyOneResponseCode


class DataSet(BaseModel):
    data_id: str = Field(..., alias="id")
    data_type: DataSetResultTypes = Field(...)
    name: str = Field(...)
    data_dir: str = Field(...)

    @validator("data_dir")
    def check_dir(cls, v):
        base_path = Path(conf.base_path)
        if Path.exists(base_path / v):
            return v
        logger.error(f"{v} does not exist")
        raise ValueError(f"{v} is not a valid directory")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "32423xfcd33xxx",
                "name": "ymir_data233",
                "data_type": 0,
                "data_dir": "ymir-workplace/voc",
            }
        }


class Task(BaseModel):
    tid: str
    datas: List[DataSet]

    @validator("datas")
    def check_ground_truth_once(cls, v):
        type_cnt = Counter(d.data_type for d in v)
        if type_cnt[DataSetResultTypes.GROUND_TRUTH] > 1:
            raise ValueError(
                f"Only one ground truth dataset is allowed. Found {type_cnt[DataSetResultTypes.GROUND_TRUTH]}."
            )
        return v


class BaseResponse(BaseModel):
    code: int = FiftyOneResponseCode.FO_OK
    error: str = ""

    class Config:
        schema_extra = {
            "example": {
                "code": FiftyOneResponseCode.FO_OK,
                "error": "",
            }
        }


class TaskCreateBody(BaseModel):
    tid: str = ""


class TaskCreateResponse(BaseResponse):
    data: TaskCreateBody = TaskCreateBody()


class TaskQueryBody(BaseModel):
    status: int = FiftyoneTaskStatus.PENDING.value
    url: str = ""


class TaskQueryResponse(BaseResponse):
    data: TaskQueryBody = TaskQueryBody()


class TaskDeleteResponse(BaseResponse):
    data: dict = {}


class ErrorResponse(BaseResponse):
    data: dict = {}
