import random
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.errors.errors import (
    FailedtoDownloadError,
    InvalidInferenceConfig,
    ModelNotFound,
)
from app.config import settings
from tests.utils.images import create_docker_image_and_configs
from tests.utils.models import create_model
from tests.utils.utils import random_lower_string, random_url


class TestPostInference:
    def test_call_inference_missing_model(self, client: TestClient, normal_user_token_headers: Dict[str, str], mocker):
        j = {
            "model_id": random.randint(1000, 2000),
            "docker_image": random_lower_string(),
            "image_urls": [random_url()],
            "docker_image_config": {"mock_docker_image_config": "mock_docker_image_config"},
        }
        r = client.post(
            f"{settings.API_V1_STR}/inferences/",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.json()["code"] == ModelNotFound.code

    def test_call_inference_invalid_docker(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = create_model(db, user_id)
        j = {
            "model_id": model.id,
            "docker_image": random_lower_string(),
            "image_urls": [random_url()],
            "docker_image_config": {"mock_docker_image_config": "mock_docker_image_config"},
        }
        r = client.post(
            f"{settings.API_V1_STR}/inferences/",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.json()["code"] == InvalidInferenceConfig.code

    def test_call_inference_download_error(
        self,
        db: Session,
        client: TestClient,
        user_id: int,
        normal_user_token_headers: Dict[str, str],
        mocker,
    ):
        model = create_model(db, user_id)
        image, config = create_docker_image_and_configs(db, image_type=9)
        j = {
            "model_id": model.id,
            "docker_image": image.url,
            "image_urls": [random_url()],
            "docker_image_config": {"mock_docker_image_config": "mock_docker_image_config"},
        }
        r = client.post(
            f"{settings.API_V1_STR}/inferences/",
            headers=normal_user_token_headers,
            json=j,
        )
        assert r.json()["code"] == FailedtoDownloadError.code
