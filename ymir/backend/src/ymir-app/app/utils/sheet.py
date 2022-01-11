import abc
from typing import Dict, List, Optional

from requests import PreparedRequest, Request, Response, Session

from app.config import settings


class OnlineSheetAPI(abc.ABC):
    @abc.abstractmethod
    def prepare_request(self) -> PreparedRequest:
        """
        different online sheet api requires various request
        """

    def send(self, timeout: int = settings.SHARING_TIMEOUT) -> Response:
        s = Session()
        req = self.prepare_request()
        resp = s.send(req, timeout=timeout)
        return resp


class WufooAPI(OnlineSheetAPI):
    def __init__(self, payload: Dict):
        self.data = {
            "Field1": payload["docker_name"],
            "Field2": payload["submitter"],
            "Field3": payload["phone"],
            "Field4": payload["email"],
            "Field5": payload["organization"],
        }

    def prepare_request(self) -> PreparedRequest:
        url = settings.WUFOO_URL
        headers = {"Authorization": settings.WUFOO_AUTHORIZATION}
        req = Request("POST", url, headers=headers, data=self.data)
        return req.prepare()
