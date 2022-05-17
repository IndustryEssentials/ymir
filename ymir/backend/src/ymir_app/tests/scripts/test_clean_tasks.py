from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app import clean_tasks as m
from app.constants.state import TaskState
from tests.utils.tasks import create_task


def test_list_unfinished_tasks(db: Session, mocker: Any) -> None:
    user_id = randint(100, 200)
    task = create_task(db, user_id, state=TaskState.running)
    tasks = m.list_unfinished_tasks(db)
    assert task.id in [t.id for t in tasks]
