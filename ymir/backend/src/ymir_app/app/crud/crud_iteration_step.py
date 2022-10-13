import json
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
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        steps_in_same_iteration = self.get_multi_by_iteration(db, iteration_id=step.iteration_id)
        current_idx = [i.id for i in steps_in_same_iteration].index(step.id)
        return steps_in_same_iteration[current_idx - 1]

    def start(self, db: Session, id: int, task_id: int, task_parameters: Optional[str]) -> IterationStep:
        """
        start given iteration_step:
        1. create task
        2. save task result in related step
        """
        step = self.get(db, id)
        if not step:
            raise StepNotFound()
        updates = {"task_id": task_id, "task_parameters": task_parameters}
        return self.update(db, db_obj=step, obj_in=updates)

    def finish(self, db: Session, id: int) -> IterationStep:
        step = self.get(db, id)
        if not step:
            raise StepNotFound()

        if step.state == ResultState.ready:
            # save result as input of next step when possible
            next_step = self.get_next_step(db, step.id)
            if next_step:
                if step.result:
                    task_parameters = json.loads(next_step.task_parameters) if next_step.task_parameters else {}
                    if step.result_dataset:
                        task_parameters["dataset_id"] = step.result_dataset.id
                    if step.result_model:
                        task_parameters["model_id"] = step.result_model.id
                    self.update(db, db_obj=next_step, obj_in={"task_parameters": json.dumps(task_parameters)})

        # set current step as finished no matter what
        return self.update(db, db_obj=step, obj_in={"is_finished": True})


iteration_step = CRUDIterationStep(IterationStep)
