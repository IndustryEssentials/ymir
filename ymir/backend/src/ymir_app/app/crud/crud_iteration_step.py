import json
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.constants.state import ResultState
from app.models.iteration_step import IterationStep
from app.schemas.iteration_step import IterationStepCreate, IterationStepUpdate


class StepNotFound(Exception):
    pass


class CRUDIterationStep(CRUDBase[IterationStep, IterationStepCreate, IterationStepUpdate]):
    def get_next_step(self, db: Session, id: int) -> Optional[IterationStep]:
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        steps_in_same_iteration = self.get_multi_by_iteration(db, iteration_id=step.iteration_id)
        current_idx = [i.id for i in steps_in_same_iteration].index(step.id)
        return steps_in_same_iteration[current_idx - 1]

    def bind_task(self, db: Session, id: int, task_id: int) -> IterationStep:
        """
        start given iteration_step:
        1. create task
        2. save task result in related step
        """
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        updates = {"task_id": task_id}
        return self.update(db, db_obj=step, obj_in=updates)

    def unbind_task(self, db: Session, id: int) -> IterationStep:
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        step.task_id = None
        db.add(step)
        db.commit()
        db.refresh(step)
        return step

    def finish(self, db: Session, id: int) -> IterationStep:
        step = self.get(db, id)
        if not step:
            raise StepNotFound()

        if step.state == ResultState.ready:
            # save result as task presetting for next_step
            next_step = self.get_next_step(db, step.id)
            if next_step and step.result:
                extra_presetting = {
                    "dataset_id": step.result_dataset.id if step.result_dataset else None,
                    "model_id": step.result_model.id if step.result_model else None,
                }
                self.update_presetting(db, next_step.id, extra_presetting)

        # set current step as finished no matter what
        db.refresh(step)
        return self.update(db, db_obj=step, obj_in={"is_finished": True})

    def update_presetting(self, db: Session, id: int, presetting: Dict) -> IterationStep:
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        step.serialized_presetting = json.dumps({**presetting, **step.presetting})
        db.add(step)
        db.commit()
        db.refresh(step)
        return step


iteration_step = CRUDIterationStep(IterationStep)
