# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from src.swagger_models.base_model_ import Model
from src.swagger_models.api_response import ApiResponse  # noqa: F401,E501
from src.swagger_models.assets_meta_info import AssetsMetaInfo  # noqa: F401,E501
from src import util


class AssetMetaResult(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, code: int=None, request_id: str=None, message: str=None, result: AssetsMetaInfo=None):  # noqa: E501
        """AssetMetaResult - a model defined in Swagger

        :param code: The code of this AssetMetaResult.  # noqa: E501
        :type code: int
        :param request_id: The request_id of this AssetMetaResult.  # noqa: E501
        :type request_id: str
        :param message: The message of this AssetMetaResult.  # noqa: E501
        :type message: str
        :param result: The result of this AssetMetaResult.  # noqa: E501
        :type result: AssetsMetaInfo
        """
        self.swagger_types = {
            'code': int,
            'request_id': str,
            'message': str,
            'result': AssetsMetaInfo
        }

        self.attribute_map = {
            'code': 'code',
            'request_id': 'request_id',
            'message': 'message',
            'result': 'result'
        }
        self._code = code
        self._request_id = request_id
        self._message = message
        self._result = result

    @classmethod
    def from_dict(cls, dikt) -> 'AssetMetaResult':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AssetMetaResult of this AssetMetaResult.  # noqa: E501
        :rtype: AssetMetaResult
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self) -> int:
        """Gets the code of this AssetMetaResult.


        :return: The code of this AssetMetaResult.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code: int):
        """Sets the code of this AssetMetaResult.


        :param code: The code of this AssetMetaResult.
        :type code: int
        """

        self._code = code

    @property
    def request_id(self) -> str:
        """Gets the request_id of this AssetMetaResult.


        :return: The request_id of this AssetMetaResult.
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id: str):
        """Sets the request_id of this AssetMetaResult.


        :param request_id: The request_id of this AssetMetaResult.
        :type request_id: str
        """

        self._request_id = request_id

    @property
    def message(self) -> str:
        """Gets the message of this AssetMetaResult.


        :return: The message of this AssetMetaResult.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this AssetMetaResult.


        :param message: The message of this AssetMetaResult.
        :type message: str
        """

        self._message = message

    @property
    def result(self) -> AssetsMetaInfo:
        """Gets the result of this AssetMetaResult.


        :return: The result of this AssetMetaResult.
        :rtype: AssetsMetaInfo
        """
        return self._result

    @result.setter
    def result(self, result: AssetsMetaInfo):
        """Sets the result of this AssetMetaResult.


        :param result: The result of this AssetMetaResult.
        :type result: AssetsMetaInfo
        """

        self._result = result
