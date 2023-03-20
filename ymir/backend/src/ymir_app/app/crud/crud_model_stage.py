from typing import Any, Optional, List
from sqlalchemy.orm import Session

from app.api.errors.errors import InvalidModelStageName, ModelStageNotFound
from app.crud.base import CRUDBase
from app.models import ModelStage, Model
from app.schemas.model_stage import ModelStageCreate, ModelStageUpdate


class CRUDModelStage(CRUDBase[ModelStage, ModelStageCreate, ModelStageUpdate]):
    def get(self, db: Session, id: Any) -> Optional[ModelStage]:
        stage = db.query(self.model).filter(self.model.id == id).first()
        if stage and not is_valid_model_stage_name(stage.name):
            raise InvalidModelStageName()
        return stage

    def get_multi_by_user_and_ids(self, db: Session, *, user_id: int, ids: List[int]) -> List[ModelStage]:
        if len(ids) == 0:
            return []
        query = (
            db.query(self.model)
            .filter(self.model.id.in_(ids))
            .join(Model, Model.id == self.model.model_id)
            .filter(Model.user_id == user_id)
        )
        if len(ids) != query.count():
            raise ModelStageNotFound()
        return query.all()


def is_valid_model_stage_name(name: Optional[str]) -> bool:
    if not name:
        return False
    return name.isidentifier()


model_stage = CRUDModelStage(ModelStage)
