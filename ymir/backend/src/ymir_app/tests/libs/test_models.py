from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app.libs import models as m
from app.constants.state import ResultState
from tests.utils.utils import random_lower_string
from tests.utils.models import create_model


class TestImportModel:
    def test_import_model_in_background(self, db: Session, mocker: Any) -> None:
        ctrl = mocker.Mock()
        model_import = mocker.Mock()
        user_id = randint(100, 200)
        model = create_model(db, user_id)
        assert model.result_state == ResultState.processing
        task_hash = random_lower_string()
        mock_import = mocker.Mock(side_effect=ValueError)
        m._import_model = mock_import
        m.import_model_in_background(db, ctrl, model_import, user_id, task_hash, model.id)
        assert model.result_state == ResultState.error
        mock_import.assert_called()
