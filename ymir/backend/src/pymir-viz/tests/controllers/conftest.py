import json

import pytest
from flask import Response
from flask.testing import FlaskClient


class APIResponse(Response):
    def json(self):
        return json.loads(self.data)


@pytest.fixture()
def test_client(core_app):
    core_app.test_client_class = FlaskClient
    core_app.response_class = APIResponse
    return core_app.test_client()
