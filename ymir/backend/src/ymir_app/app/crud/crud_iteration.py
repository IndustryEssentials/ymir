from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Iteration
from app.schemas.iteration import IterationCreate, IterationUpdate
from app.api.errors.errors import IterationNotFound


class CRUDIteration(CRUDBase[Iteration, IterationCreate, IterationUpdate]):
    def update_iteration(self, db: Session, *, iteration_id: int, iteration_update: IterationUpdate) -> Iteration:
        iteration = self.get(db, id=iteration_id)
        if not iteration:
            raise IterationNotFound()
        return self.update(db, db_obj=iteration, obj_in=iteration_update)


iteration = CRUDIteration(Iteration)
