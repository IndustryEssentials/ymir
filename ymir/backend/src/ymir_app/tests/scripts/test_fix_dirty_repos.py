from typing import Any
from sqlalchemy.orm import Session

from app import fix_dirty_repos as m
from tests.utils.projects import create_project_record


def test_iter_all_repos(db: Session) -> None:
    project = create_project_record(db)
    projects = list(m.iter_all_projects(db))
    assert project.id in [p.id for ps in projects for p in ps]


def test_fix_repo(db: Session, mocker: Any) -> None:
    ctrl = mocker.Mock()
    mocker.patch.object(m, "ControllerClient", return_value=ctrl)
    project = create_project_record(db)
    m.fix_repo(ctrl, project)
    ctrl.fix_repo.assert_called_with(user_id=project.user_id, project_id=project.id)
