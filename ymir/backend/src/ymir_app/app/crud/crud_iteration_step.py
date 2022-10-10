from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.constants.state import ResultState
from app.models.iteration_step import IterationStep
from app.schemas.iteration_step import IterationStepCreate, IterationStepUpdate


class StepNotFound(Exception):
    pass


class CRUDIterationStep(CRUDBase[IterationStep, IterationStepCreate, IterationStepUpdate]):
    def get_next_step(self, db: Session, id: int) -> Optional[IterationStep]:
        step = self.get(db, id=id)
        if not step:
            raise StepNotFound()
        steps_in_same_iteration = self.get_multi_by_iteration(db, iteration_id=step.iteration_id)
        current_idx = [i.id for i in steps_in_same_iteration].index(step.id)
        return steps_in_same_iteration[current_idx - 1]

    def record_result(
        self, db: Session, id: int, task_id: int, result_dataset_id: Optional[int], result_model_id: Optional[int]
    ) -> IterationStep:
        """
        start given iteration_step:
        1. create task
        2. save task result in related step
        """
        step = self.get(db, id=id)
        if not step:
            raise StepNotFound()
        updates = {"task_id": task_id, "output_dataset_id": result_dataset_id, "output_model_id": result_model_id}
        updates = {k: v for k, v in updates.items() if v is not None}
        return self.update(db, db_obj=step, obj_in=updates)

    def finish(self, db: Session, id: int) -> IterationStep:
        step = self.get(db, id=id)
        if not step:
            raise StepNotFound()

        if step.state == ResultState.ready:
            # save result as input of next step when possible
            next_step = self.get_next_step(db, step.id)
            if next_step:
                self.update(db, db_obj=next_step, obj_in={"input_dataset_id": step.output_dataset_id})

        # set current step as finished no matter what
        return self.update(db, db_obj=step, obj_in={"is_finished": True})


iteration_step = CRUDIterationStep(IterationStep)
