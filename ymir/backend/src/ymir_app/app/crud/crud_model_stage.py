from app.crud.base import CRUDBase
from app.models import ModelStage
from app.schemas.model_stage import ModelStageCreate, ModelStageUpdate


class CRUDModelStage(CRUDBase[ModelStage, ModelStageCreate, ModelStageUpdate]):
    pass


model_stage = CRUDModelStage(ModelStage)
