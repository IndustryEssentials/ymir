from typing import Any

from fastapi.logger import logger
from requests import Session, Response
from requests.exceptions import HTTPError

from yapi.api.errors.errors import InvalidModel, APIError
from yapi.config import settings
from yapi.schemas.user import UserInfo


class AppClient(Session):
    def __init__(self, user_info: UserInfo, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)  # type: ignore
        self.headers = {
            "X-User-Id": str(user_info.id),
            "X-User-Role": str(user_info.role.value),
        }

    def request(self, *args: Any, **kwargs: Any) -> Response:
        """
        ymir app alyways return 200, we have to raise exception manually
        """
        response = super().request(*args, **kwargs)
        try:
            app_resp = response.json()
        except Exception:
            logger.exception("Unknown ymir_app error")
            raise HTTPError()
        if app_resp["code"] != 0:
            raise APIError(detail=app_resp)
        return response


def must_get_model_stage_id(app: AppClient, model_version_id: int) -> int:
    model_info = app.get(f"{settings.APP_URL_PREFIX}/models/{model_version_id}")
    try:
        return model_info.json()["result"]["recommended_stage"]
    except Exception:
        logger.exception("Failed to must_get_model_stage_id(app, %s)", model_version_id)
        raise InvalidModel()
