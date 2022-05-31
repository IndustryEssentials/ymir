from typing import List, Union

from pydantic import BaseModel, Field


class DataSet(BaseModel):
    id: str
    name: str = Field(...)
    data_dir: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "id": "32423xfcd33xxx",
                "name": "ymir_data233",
                "data_dir": "./data/ymir_data233",
            }
        }


class Task(BaseModel):
    tid: str
    datas: Union[List[DataSet]]


class BaseResponse(BaseModel):
    code: int = 0
    error: str = ""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "id": "32423xfcd33xxx",
                "code": 0,
                "error": "",
            }
        }


class BaseResponseBody:
    def __init__(self):
        self.code = 0
        self.data = {}
        self.error = None

    @property
    def dict(self):
        return self.__dict__


class TaskCreateBody(BaseModel):
    tid: str


class TaskCreateResponse(BaseResponse):
    data: TaskCreateBody
