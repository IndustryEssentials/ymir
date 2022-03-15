from app.crud.base import CRUDBase
from app.models import Iteration
from app.schemas.iteration import IterationCreate, IterationUpdate


class CRUDIteration(CRUDBase[Iteration, IterationCreate, IterationUpdate]):
    pass


iteration = CRUDIteration(Iteration)
