import logging
import os
import shutil
from typing import List
import unittest

from controller.utils import labels

import tests.utils as test_utils


class TestLabelFileHandler(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._test_root, exist_ok=True)
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        return super().tearDown()

    # protected: check result
    def _check_result(self, expected: List[dict], actual: List[dict]) -> None:
        try:
            expected_length = len(expected)
            self.assertEqual(expected_length, len(actual))
            for idx in range(expected_length):
                expected_label = expected[idx]
                actual_label = actual[idx]
                is_modified = expected_label['_is_modified']

                self.assertEqual(expected_label[labels.kLabelId], actual_label[labels.kLabelId])
                self.assertEqual(actual_label[labels.kLabelId], idx)
                self.assertEqual(expected_label[labels.kLabelName], actual_label[labels.kLabelName])
                self.assertEqual(expected_label.get(labels.kLabelAliases, []),
                                 actual_label.get(labels.kLabelAliases, []))

                self.assertGreater(actual_label[labels.kLabelCreated], 0)
                if is_modified:
                    # if modified, modified time >= created time
                    self.assertGreater(actual_label[labels.kLabelModified], actual_label[labels.kLabelCreated])
                else:
                    # if new, they should be equal
                    self.assertEqual(actual_label[labels.kLabelModified], actual_label[labels.kLabelCreated])
        except AssertionError as e:
            logging.error(f"ground: {expected}")
            logging.error(f"actual: {actual}")
            raise e

    # public: test cases
    def test_merge(self):
        label_handler = labels.LabelFileHandler(mir_root=self._test_root)

        # case 0: add 3 new labels
        candidate_labels = ['a,aa,aaa', 'h,hh,hhh', 'z']
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=False)
        expected = [{
            labels.kLabelId: 0,
            labels.kLabelName: 'a',
            labels.kLabelAliases: ['aa', 'aaa'],
            '_is_modified': False
        }, {
            labels.kLabelId: 1,
            labels.kLabelName: 'h',
            labels.kLabelAliases: ['hh', 'hhh'],
            '_is_modified': False
        }, {
            labels.kLabelId: 2,
            labels.kLabelName: 'z',
            '_is_modified': False
        }]
        self.assertFalse(conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())

        # a unchanged, m with a conflicted alias hh, so all merge is ignored
        # no change will made to storage file
        candidate_labels = ['a,aa,aaa', 'm,hh', 'zz']
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=False)
        self.assertEqual([['m', 'hh']], conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())

        # a: reset aliases, h: reset aliases, x: add new, z: unchanged
        candidate_labels = ["A,aa", "h", "x,xx,xxx"]
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=False)
        expected = [{
            labels.kLabelId: 0,
            labels.kLabelName: 'a',
            labels.kLabelAliases: ['aa'],
            '_is_modified': True
        }, {
            labels.kLabelId: 1,
            labels.kLabelName: 'h',
            '_is_modified': True
        }, {
            labels.kLabelId: 2,
            labels.kLabelName: 'z',
            '_is_modified': False
        }, {
            labels.kLabelId: 3,
            labels.kLabelName: 'x',
            labels.kLabelAliases: ['xx', 'xxx'],
            '_is_modified': False
        }]
        self.assertFalse(conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())

        # h: reset aliases with conflict, so all merge is ignored, storage file unchanged
        candidate_labels = ["h,a"]
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=False)
        self.assertEqual([['h', 'a']], conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())

        # checkonly, wants to add c
        candidate_labels = ['c,cc,ccc']
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=True)
        self.assertFalse(conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())

        # add again
        candidate_labels = ['c,cc,ccc']
        conflict_labels = label_handler.merge_labels(candidate_labels, check_only=False)
        expected = [{
            labels.kLabelId: 0,
            labels.kLabelName: 'a',
            labels.kLabelAliases: ['aa'],
            '_is_modified': True
        }, {
            labels.kLabelId: 1,
            labels.kLabelName: 'h',
            '_is_modified': True
        }, {
            labels.kLabelId: 2,
            labels.kLabelName: 'z',
            '_is_modified': False
        }, {
            labels.kLabelId: 3,
            labels.kLabelName: 'x',
            labels.kLabelAliases: ['xx', 'xxx'],
            '_is_modified': False
        }, {
            labels.kLabelId: 4,
            labels.kLabelName: 'c',
            labels.kLabelAliases: ['cc', 'ccc'],
            '_is_modified': False
        }]
        self.assertFalse(conflict_labels)
        self._check_result(expected=expected, actual=label_handler.get_all_labels())
