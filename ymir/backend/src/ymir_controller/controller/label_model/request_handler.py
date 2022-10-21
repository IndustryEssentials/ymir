from typing import Dict

import requests

from controller.config import label_task as label_task_config


class RequestHandler:
    def __init__(
        self,
        url: str = label_task_config.LABEL_TOOL_HOST_URL,
        headers: Dict[str, str] = {"Authorization": label_task_config.LABEL_TOOL_TOKEN},
    ):
        self.url = url
        self.headers = headers
        self.timeout = label_task_config.LABEL_TOOL_TIMEOUT

    def get(self, url_path: str, params: Dict = {}) -> bytes:
        resp = requests.get(url=f"{self.url}{url_path}", headers=self.headers, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content

    def post(self, url_path: str, params: Dict = {}, json_data: Dict = {}) -> bytes:
        resp = requests.post(
            url=f"{self.url}{url_path}", headers=self.headers, params=params, json=json_data, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.content

    def put(self, url_path: str, params: Dict = {}) -> bytes:
        resp = requests.put(url=f"{self.url}{url_path}", headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.content
