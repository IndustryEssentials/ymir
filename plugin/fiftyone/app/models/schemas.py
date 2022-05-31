from typing import List

from pydantic import BaseModel, Field

from utils.errors import FiftyOneResponseCode


class DataSet(BaseModel):
    data_id: str = Field(..., alias="id")
    name: str = Field(...)
    data_dir: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "32423xfcd33xxx",
                "name": "ymir_data233",
                "data_dir": "./data/ymir_data233",
            }
        }


class Task(BaseModel):
    tid: str
    datas: List[DataSet]


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


class ErrorResponse(BaseResponse):
    data: dict = {}
