from pydantic import BaseModel


class TaskVisualRelationshipCreate(BaseModel):
    task_id: int
    visualization_id: int

    class Config:
        use_enum_values = True
        validate_all = True


class TaskVisualRelationshipUpdate(BaseModel):
    pass
