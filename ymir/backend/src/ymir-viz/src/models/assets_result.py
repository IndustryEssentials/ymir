# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from src import util
from src.models.api_response import ApiResponse  # noqa: F401,E501
from src.models.assets_result_result import AssetsResultResult  # noqa: F401,E501
from src.models.base_model_ import Model


class AssetsResult(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        code: int = None,
        request_id: str = None,
        message: str = None,
        result: AssetsResultResult = None,
    ):  # noqa: E501
        """AssetsResult - a model defined in Swagger

        :param code: The code of this AssetsResult.  # noqa: E501
        :type code: int
        :param request_id: The request_id of this AssetsResult.  # noqa: E501
        :type request_id: str
        :param message: The message of this AssetsResult.  # noqa: E501
        :type message: str
        :param result: The result of this AssetsResult.  # noqa: E501
        :type result: AssetsResultResult
        """
        self.swagger_types = {
            "code": int,
            "request_id": str,
            "message": str,
            "result": AssetsResultResult,
        }

        self.attribute_map = {
            "code": "code",
            "request_id": "request_id",
            "message": "message",
            "result": "result",
        }
        self._code = code
        self._request_id = request_id
        self._message = message
        self._result = result

    @classmethod
    def from_dict(cls, dikt) -> "AssetsResult":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AssetsResult of this AssetsResult.  # noqa: E501
        :rtype: AssetsResult
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self) -> int:
        """Gets the code of this AssetsResult.


        :return: The code of this AssetsResult.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code: int):
        """Sets the code of this AssetsResult.


        :param code: The code of this AssetsResult.
        :type code: int
        """

        self._code = code

    @property
    def request_id(self) -> str:
        """Gets the request_id of this AssetsResult.


        :return: The request_id of this AssetsResult.
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id: str):
        """Sets the request_id of this AssetsResult.


        :param request_id: The request_id of this AssetsResult.
        :type request_id: str
        """

        self._request_id = request_id

    @property
    def message(self) -> str:
        """Gets the message of this AssetsResult.


        :return: The message of this AssetsResult.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this AssetsResult.


        :param message: The message of this AssetsResult.
        :type message: str
        """

        self._message = message

    @property
    def result(self) -> AssetsResultResult:
        """Gets the result of this AssetsResult.


        :return: The result of this AssetsResult.
        :rtype: AssetsResultResult
        """
        return self._result

    @result.setter
    def result(self, result: AssetsResultResult):
        """Sets the result of this AssetsResult.


        :param result: The result of this AssetsResult.
        :type result: AssetsResultResult
        """

        self._result = result
