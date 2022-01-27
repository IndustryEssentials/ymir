import glob
import json
import math
import os
import shutil
import zipfile
from io import BytesIO
from typing import Dict, List
from xml.etree import ElementTree

import requests

from controller.config import label_task as label_task_config
from controller.label_model.base import LabelBase, catch_label_task_error
from controller.utils.app_logger import logger


class RequestHandler:
    def __init__(
        self,
        url: str = label_task_config.LABEL_TOOL_URL,
        headers: Dict[str, str] = {"Authorization": label_task_config.LABEL_TOOL_TOKEN},
    ):
        self.url = url
        self.headers = headers

    def get(self, url_path: str, params: Dict = {}) -> bytes:
        resp = requests.get(url=f"{self.url}{url_path}", headers=self.headers, params=params, timeout=600)
        resp.raise_for_status()
        return resp.content

    def post(self, url_path: str, params: Dict = {}, json_data: Dict = {}) -> bytes:
        resp = requests.post(
            url=f"{self.url}{url_path}", headers=self.headers, params=params, json=json_data, timeout=600
        )
        resp.raise_for_status()
        return resp.content
