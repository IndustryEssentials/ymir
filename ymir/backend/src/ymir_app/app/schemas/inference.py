from typing import Dict, List, Optional

from pydantic import BaseModel, Field, root_validator

from app.schemas.common import Common


class InferenceBase(BaseModel):
    docker_image: str
    project_id: int
    model_stage_id: int
    image_urls: List[str]
    docker_image_config: Dict = Field(description="inference docker image runtime configuration")


class InferenceCreate(InferenceBase):
    pass


class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int


class PolygonPoint(BaseModel):
    x: int
    y: int
    z: int


class InferredAnnotation(BaseModel):
    box: Box
    mask: Optional[str]
    polygon: List[PolygonPoint]
    class_name: str
    keyword: str = Field(description="aka class_name for MIR")
    score: float = Field(ge=0, le=1)

    @root_validator(pre=True)
    def fill_keyword(cls, values: Dict) -> Dict:
        # rename class_name to keyword
        values["keyword"] = values["class_name"]
        return values


class Annotation(BaseModel):
    image_url: str
    annotations: List[InferredAnnotation]


class InferenceResult(BaseModel):
    model_stage_id: int
    annotations: List[Annotation]


class InferenceOut(Common):
    result: InferenceResult
