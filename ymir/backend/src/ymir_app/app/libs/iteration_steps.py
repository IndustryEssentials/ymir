from typing import List

from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.constants.state import IterationStepTemplates


def initialize_steps(db: Session, iteration_id: int) -> List[models.IterationStep]:
    """
    initialize all the necessary steps upon new iteration
    """
    steps = [
        schemas.iteration_step.IterationStepCreate(
            iteration_id=iteration_id, name=step_template.name, task_type=step_template.task_type
        )
        for step_template in IterationStepTemplates
    ]
    return crud.iteration_step.batch_create(db, objs_in=steps)
