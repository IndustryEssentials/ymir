# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from src.swagger_models.base_model_ import Model
from src.swagger_models.dataset_evaluation_element import DatasetEvaluationElement  # noqa: F401,E501
from src import util


class DatasetEvaluationTotalSubElement(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, total: DatasetEvaluationElement=None, sub: Dict[str, DatasetEvaluationElement]=None):  # noqa: E501
        """DatasetEvaluationTotalSubElement - a model defined in Swagger

        :param total: The total of this DatasetEvaluationTotalSubElement.  # noqa: E501
        :type total: DatasetEvaluationElement
        :param sub: The sub of this DatasetEvaluationTotalSubElement.  # noqa: E501
        :type sub: Dict[str, DatasetEvaluationElement]
        """
        self.swagger_types = {
            'total': DatasetEvaluationElement,
            'sub': Dict[str, DatasetEvaluationElement]
        }

        self.attribute_map = {
            'total': 'total',
            'sub': 'sub'
        }
        self._total = total
        self._sub = sub

    @classmethod
    def from_dict(cls, dikt) -> 'DatasetEvaluationTotalSubElement':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DatasetEvaluationTotalSubElement of this DatasetEvaluationTotalSubElement.  # noqa: E501
        :rtype: DatasetEvaluationTotalSubElement
        """
        return util.deserialize_model(dikt, cls)

    @property
    def total(self) -> DatasetEvaluationElement:
        """Gets the total of this DatasetEvaluationTotalSubElement.


        :return: The total of this DatasetEvaluationTotalSubElement.
        :rtype: DatasetEvaluationElement
        """
        return self._total

    @total.setter
    def total(self, total: DatasetEvaluationElement):
        """Sets the total of this DatasetEvaluationTotalSubElement.


        :param total: The total of this DatasetEvaluationTotalSubElement.
        :type total: DatasetEvaluationElement
        """

        self._total = total

    @property
    def sub(self) -> Dict[str, DatasetEvaluationElement]:
        """Gets the sub of this DatasetEvaluationTotalSubElement.


        :return: The sub of this DatasetEvaluationTotalSubElement.
        :rtype: Dict[str, DatasetEvaluationElement]
        """
        return self._sub

    @sub.setter
    def sub(self, sub: Dict[str, DatasetEvaluationElement]):
        """Sets the sub of this DatasetEvaluationTotalSubElement.


        :param sub: The sub of this DatasetEvaluationTotalSubElement.
        :type sub: Dict[str, DatasetEvaluationElement]
        """

        self._sub = sub
