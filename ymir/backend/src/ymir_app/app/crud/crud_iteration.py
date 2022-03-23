from typing import List

from sqlalchemy import not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Iteration
from app.schemas.iteration import IterationCreate, IterationUpdate
from app.api.errors.errors import IterationNotFound


class CRUDIteration(CRUDBase[Iteration, IterationCreate, IterationUpdate]):
    def get_multi_iterations(
        self,
        db: Session,
        *,
        project_id: int,
    ) -> List[Iteration]:
        query = db.query(self.model)
        query = query.filter(self.model.project_id == project_id, not_(self.model.is_deleted))

        return query.all()

    def update_iteration(self, db: Session, *, iteration_id: int, iteration_update: IterationUpdate) -> Iteration:
        iteration = self.get(db, id=iteration_id)
        if not iteration:
            raise IterationNotFound()
        return self.update(db, db_obj=iteration, obj_in=iteration_update)


iteration = CRUDIteration(Iteration)
