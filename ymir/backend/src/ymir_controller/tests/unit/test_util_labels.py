import logging
import os
import shutil
from typing import List
import unittest

from common_utils import labels

import tests.utils as test_utils


class TestLabelFileHandler(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        # dir structure:
        # test_involer_CLSNAME_sandbox_root
        # ├── media_storage_root
        # └── test_user
        #     └── ymir-dvc-test
        super().__init__(methodName=methodName)
        self._user_name = "user"
        self._mir_repo_name = "repoid"
        self._storage_name = "media_storage_root"
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz5'
        self._base_task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._label_storage_file = os.path.join(self._user_root, 'labels.yaml')
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        labels.create_empty(label_storage_file=self._label_storage_file)
        logging.info("preparing done.")

    def tearDown(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        pass

    # custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            logging.info("sandbox root exists, remove it first")
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._storage_root)

    # protected: check result
    def _check_result(self, expected: List[dict], actual: List[labels.SingleLabel]) -> None:
        try:
            expected_length = len(expected)
            self.assertEqual(expected_length, len(actual))
            for idx in range(expected_length):
                expected_label: labels.SingleLabel = expected[idx]['_label']
                is_modified: bool = expected[idx]['_is_modified']
                actual_label = actual[idx]

                self.assertEqual(expected_label.id, actual_label.id)
                self.assertEqual(actual_label.id, idx)
                self.assertEqual(expected_label.name, actual_label.name)
                self.assertEqual(expected_label.aliases, actual_label.aliases)

                if is_modified:
                    # if modified, update time >= create time
                    assert actual_label.update_time >= actual_label.create_time
                else:
                    # if new, they should be equal
                    assert actual_label.update_time == actual_label.create_time
        except AssertionError as e:
            logging.error(f"ground: {expected}")
            logging.error(f"actual: {actual}")
            raise e

    # public: test cases
    def test_merge(self):
        # case 0: add 3 new labels
        candidate_labels_1 = labels.UserLabels.parse_obj({
            'labels': [{
                'name': 'a',
                'aliases': ['aa', 'aaa']
            }, {
                'name': 'h',
                'aliases': ['hh', 'hhh']
            }, {
                'name': 'z',
                'aliases': []
            }]
        })
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_1,
                                              check_only=False)
        expected = [{
            '_label': labels.SingleLabel(id=0, name='a', aliases=['aa', 'aaa']),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=1, name='h', aliases=['hh', 'hhh']),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=2, name='z'),
            '_is_modified': False,
        }]
        self.assertFalse(conflict_labels.labels)
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # a unchanged, m with a conflicted alias hh, so all merge is ignored
        # no change will made to storage file
        candidate_labels_2 = labels.UserLabels.parse_obj({
            'labels': [{
                'name': 'a',
                'aliases': ['aa', 'aaa']
            }, {
                'name': 'm',
                'aliases': ['hh']
            }, {
                'name': 'zz',
                'aliases': []
            }]
        })
        # candidate_labels = ['a,aa,aaa', 'm,hh', 'zz']
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_2,
                                              check_only=False)
        conflict_labels_expected = labels.UserLabels.parse_obj({'labels': [{'name': 'm', 'aliases': ['hh']}]})
        self.assertDictEqual(conflict_labels_expected.dict(), conflict_labels.dict())
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # a: reset aliases, h: reset aliases, x: add new, z: unchanged
        candidate_labels_3 = labels.UserLabels.parse_obj({
            'labels': [{
                'name': 'A',
                'aliases': ['aa']
            }, {
                'name': 'h',
                'aliases': []
            }, {
                'name': 'x',
                'aliases': ['xx', 'xxx']
            }]
        })
        # candidate_labels = ["A,aa", "h", "x,xx,xxx"]
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_3,
                                              check_only=False)
        expected = [{
            '_label': labels.SingleLabel(id=0, name='a', aliases=['aa']),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=1, name='h'),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=2, name='z'),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=3, name='x', aliases=['xx', 'xxx']),
            '_is_modified': False,
        }]
        self.assertFalse(conflict_labels.labels)
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # h: reset aliases with conflict, so all merge is ignored, storage file unchanged
        # candidate_labels = ["h,a"]
        candidate_labels_4 = labels.UserLabels.parse_obj({'labels': [{'name': 'h', 'aliases': ['a']}]})
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_4,
                                              check_only=False)
        conflict_labels_expected = labels.UserLabels.parse_obj({'labels': [{'name': 'h', 'aliases': ['a']}]})
        self.assertDictEqual(conflict_labels_expected.dict(), conflict_labels.dict())
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # checkonly, wants to add c
        # candidate_labels = ['c,cc,ccc']
        candidate_labels_5 = labels.UserLabels.parse_obj({'labels': [{'name': 'c', 'aliases': ['cc', 'ccc']}]})
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_5,
                                              check_only=True)
        self.assertFalse(conflict_labels.labels)
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # add again
        # candidate_labels = ['c,cc,ccc']
        candidate_labels_6 = labels.UserLabels.parse_obj({'labels': [{'name': 'c', 'aliases': ['cc', 'ccc']}]})
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_6,
                                              check_only=False)
        expected = [{
            '_label': labels.SingleLabel(id=0, name='a', aliases=['aa']),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=1, name='h'),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=2, name='z'),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=3, name='x', aliases=['xx', 'xxx']),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=4, name='c', aliases=['cc', 'ccc']),
            '_is_modified': False,
        }]
        self.assertFalse(conflict_labels.labels)
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)

        # add label with head and tail spaces
        candidate_labels_7 = labels.UserLabels.parse_obj(
            {'labels': [{
                'name': ' d ',
                'aliases': ['dd ', ' ddd', ' d d d']
            }]})
        # candidate_labels = [' d ,dd , ddd, d d d']
        conflict_labels = labels.merge_labels(label_storage_file=self._label_storage_file,
                                              new_labels=candidate_labels_7,
                                              check_only=False)
        expected = [{
            '_label': labels.SingleLabel(id=0, name='a', aliases=['aa']),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=1, name='h'),
            '_is_modified': True,
        }, {
            '_label': labels.SingleLabel(id=2, name='z'),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=3, name='x', aliases=['xx', 'xxx']),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=4, name='c', aliases=['cc', 'ccc']),
            '_is_modified': False,
        }, {
            '_label': labels.SingleLabel(id=5, name='d', aliases=['dd', 'ddd', 'd d d']),
            '_is_modified': False,
        }]
        self.assertFalse(conflict_labels.labels)
        self._check_result(expected=expected,
                           actual=labels.get_user_labels_from_storage(self._label_storage_file).labels)
