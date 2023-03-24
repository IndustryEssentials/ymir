from typing import Any

from requests import Session

from yapi.schemas.user import UserInfo


class AppClient(Session):
    def __init__(self, user_info: UserInfo, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)  # type: ignore
        self.headers = {
            "X-User-Id": str(user_info.id),
            "X-User-Role": str(user_info.role.value),
        }
