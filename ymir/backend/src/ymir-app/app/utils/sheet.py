import abc
from typing import Any, Dict, List, Optional

from requests import PreparedRequest, Request, Response, Session

from app.config import settings


class OnlineSheetAPI(abc.ABC):
    @abc.abstractmethod
    def prepare_post_request(self, payload: Dict) -> PreparedRequest:
        """
        different online sheet api requires various request
        """

    @abc.abstractmethod
    def prepare_get_request(self) -> PreparedRequest:
        """
        different online sheet api requires various request
        """

    @abc.abstractmethod
    def parse_response(self, resp: Response) -> Any:
        """
        different online sheet api requires various request
        """

    def send(self, req: PreparedRequest, timeout: int = settings.SHARING_TIMEOUT) -> Response:
        s = Session()
        resp = s.send(req, timeout=timeout)
        return resp

    def create_row(self, payload: Dict) -> Response:
        req = self.prepare_post_request(payload=payload)
        return self.send(req)

    def get_rows(self) -> Any:
        req = self.prepare_get_request()
        return self.parse_response(self.send(req))


class WufooAPI(OnlineSheetAPI):
    def __init__(
        self,
        url: Optional[str] = settings.WUFOO_URL,
        token: Optional[str] = settings.WUFOO_AUTHORIZATION,
    ):
        """
        RTFM: https://wufoo.github.io/docs/?shell#form-entries
        """
        if not (url and token):
            raise ValueError("missing Wufoo configuration")
        self.url = url
        self.token = token

        self._field_mapping = {
            "Field1": "docker_name",
            "Field2": "hash",
            "Field3": "functions",
            "Field4": "contributor",
            "Field5": "phone",
            "Field6": "email",
            "Field7": "organization",
            "Field8": "description",
        }
        self._reversed_mapping = {v: k for k, v in self._field_mapping.items()}

    def prepare_post_request(self, payload: Dict) -> PreparedRequest:
        headers = {"Authorization": self.token}
        data = {self._reversed_mapping[k]: v for k, v in payload.items() if k in self._reversed_mapping}
        req = Request("POST", self.url, headers=headers, data=data)
        return req.prepare()

    def prepare_get_request(self) -> PreparedRequest:
        headers = {"Authorization": self.token}
        filter_ = {"Filter1": "Field6 Is_equal_to checked"}
        req = Request("GET", self.url, headers=headers, params=filter_)
        return req.prepare()

    def parse_response(self, resp: Response) -> List:
        resp.raise_for_status()
        results = []
        for image_record in resp.json()["Entries"]:
            results.append({self._field_mapping.get(k, k): v for k, v in image_record.items()})
        return results
