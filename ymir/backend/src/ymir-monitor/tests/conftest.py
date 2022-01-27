import json
from typing import Dict, Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.db.session import SessionLocal
from monitor.main import app




@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

