from typing import Dict, List

from pydantic import BaseModel, Field, root_validator

from app.schemas.common import Common


class InferenceBase(BaseModel):
    docker_image: str
    model_id: int
    image_urls: List[str]
    docker_image_config: Dict = Field(description="inference docker image runtime configuration")


class InferenceCreate(InferenceBase):
    pass


class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int


class DetectionResult(BaseModel):
    box: Box
    keyword: str = Field(description="aka class_name for MIR")
    score: float = Field(ge=0, le=1)

    @root_validator(pre=True)
    def fill_keyword(cls, values: Dict) -> Dict:
        # rename class_name to keyword
        values["keyword"] = values["class_name"]
        return values


class Annotation(BaseModel):
    image_url: str
    detection: List[DetectionResult]


class InferenceResult(BaseModel):
    model_id: int
    annotations: List[Annotation]


class InferenceOut(Common):
    result: InferenceResult
