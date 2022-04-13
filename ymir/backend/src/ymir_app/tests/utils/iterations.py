from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas


def create_iteration_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    iteration_round: Optional[int] = None,
    previous_iteration: Optional[int] = None,
):
    j = {
        "project_id": project_id or randint(1000, 2000),
        "iteration_round": iteration_round or 1,
        "previous_iteration": previous_iteration or 0,
    }
    in_ = schemas.IterationCreate(**j)
    record = crud.iteration.create_with_user_id(db, obj_in=in_, user_id=user_id)
    return record
