from app.crud.base import CRUDBase
from app.models import Model
from app.schemas.model_stage import ModelStageCreate, ModelStageUpdate


class CRUDModelStage(CRUDBase[Model, ModelStageCreate, ModelStageUpdate]):
    pass


model_stage = CRUDModelStage(Model)
