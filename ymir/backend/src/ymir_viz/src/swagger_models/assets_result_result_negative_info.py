# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from src.swagger_models.base_model_ import Model
from src import util


class AssetsResultResultNegativeInfo(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, negative_images_cnt: int=None, project_negative_images_cnt: int=None):  # noqa: E501
        """AssetsResultResultNegativeInfo - a model defined in Swagger

        :param negative_images_cnt: The negative_images_cnt of this AssetsResultResultNegativeInfo.  # noqa: E501
        :type negative_images_cnt: int
        :param project_negative_images_cnt: The project_negative_images_cnt of this AssetsResultResultNegativeInfo.  # noqa: E501
        :type project_negative_images_cnt: int
        """
        self.swagger_types = {
            'negative_images_cnt': int,
            'project_negative_images_cnt': int
        }

        self.attribute_map = {
            'negative_images_cnt': 'negative_images_cnt',
            'project_negative_images_cnt': 'project_negative_images_cnt'
        }
        self._negative_images_cnt = negative_images_cnt
        self._project_negative_images_cnt = project_negative_images_cnt

    @classmethod
    def from_dict(cls, dikt) -> 'AssetsResultResultNegativeInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AssetsResult_result_negative_info of this AssetsResultResultNegativeInfo.  # noqa: E501
        :rtype: AssetsResultResultNegativeInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def negative_images_cnt(self) -> int:
        """Gets the negative_images_cnt of this AssetsResultResultNegativeInfo.


        :return: The negative_images_cnt of this AssetsResultResultNegativeInfo.
        :rtype: int
        """
        return self._negative_images_cnt

    @negative_images_cnt.setter
    def negative_images_cnt(self, negative_images_cnt: int):
        """Sets the negative_images_cnt of this AssetsResultResultNegativeInfo.


        :param negative_images_cnt: The negative_images_cnt of this AssetsResultResultNegativeInfo.
        :type negative_images_cnt: int
        """

        self._negative_images_cnt = negative_images_cnt

    @property
    def project_negative_images_cnt(self) -> int:
        """Gets the project_negative_images_cnt of this AssetsResultResultNegativeInfo.


        :return: The project_negative_images_cnt of this AssetsResultResultNegativeInfo.
        :rtype: int
        """
        return self._project_negative_images_cnt

    @project_negative_images_cnt.setter
    def project_negative_images_cnt(self, project_negative_images_cnt: int):
        """Sets the project_negative_images_cnt of this AssetsResultResultNegativeInfo.


        :param project_negative_images_cnt: The project_negative_images_cnt of this AssetsResultResultNegativeInfo.
        :type project_negative_images_cnt: int
        """

        self._project_negative_images_cnt = project_negative_images_cnt
