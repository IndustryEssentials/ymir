from typing import Any, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import ModelStage
from app.schemas.model_stage import ModelStageCreate, ModelStageUpdate


class CRUDModelStage(CRUDBase[ModelStage, ModelStageCreate, ModelStageUpdate]):
    def get(self, db: Session, id: Any) -> Optional[ModelStage]:
        stage = db.query(self.model).filter(self.model.id == id).first()
        if stage and not is_valid_model_stage_name(stage.name):
            raise ValueError("Invalid Model Stage Name")
        return stage


def is_valid_model_stage_name(name: Optional[str]) -> bool:
    if not name:
        return False
    return name.isidentifier()


model_stage = CRUDModelStage(ModelStage)
