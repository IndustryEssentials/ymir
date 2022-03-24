import logging
import os
import shutil
import unittest

import google.protobuf.json_format as pb_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import context, mir_storage_ops
from mir.tools.errors import MirError
from tests import utils as test_utils


class TestMirStorage(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self._prepare_dir()
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        return super().tearDown()

    # protected: misc
    def _prepare_dir(self):
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        os.makedirs(self._mir_root, exist_ok=True)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)

    def _prepare_mir_pb(self, with_project: bool) -> tuple:
        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_context = mirpb.MirContext()
        mir_tasks = mirpb.MirTasks()

        dict_metadatas = {
            'attributes': {
                'a001': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                'a002': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                'a003': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
            }
        }
        pb_format.ParseDict(dict_metadatas, mir_metadatas)

        dict_annotations = {
            "task_annotations": {
                "mining-task-id": {
                    "image_annotations": {
                        "a001": {
                            'annotations': [{
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 1
                            }, {
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 2
                            }]
                        },
                        "a002": {
                            'annotations': [{
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 2
                            }, {
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 3
                            }]
                        },
                        "a003": {
                            'annotations': [{
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 3
                            }, {
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 3
                            }]
                        }
                    }
                }
            }
        }
        pb_format.ParseDict(dict_annotations, mir_annotations)

        dict_keywords = {
            'keywords': {
                'a001': {
                    'predifined_keyids': [1, 2]
                },
                'a002': {
                    'predifined_keyids': [2, 3]
                },
                'a003': {
                    'predifined_keyids': [3]
                },
            },
            'index_predifined_keyids': {
                1: {
                    'asset_ids': ['a001']
                },
                2: {
                    'asset_ids': ['a001', 'a002']
                },
                3: {
                    'asset_ids': ['a002', 'a003']
                },
            }
        }
        pb_format.ParseDict(dict_keywords, mir_keywords)

        dict_context = {
            'images_cnt': 3,
            'negative_images_cnt': 0,
            'project_negative_images_cnt': (1 if with_project else 0),
            'predefined_keyids_cnt': {
                1: 1,
                2: 2,
                3: 2,
            },
            'project_predefined_keyids_cnt': ({
                3: 2,
                4: 0
            } if with_project else {}),
            'customized_keywords_cnt': {},
        }
        pb_format.ParseDict(dict_context, mir_context)

        dict_tasks = {
            'tasks': {
                'mining-task-id': {
                    'type': 'TaskTypeMining',
                    'name': 'mining',
                    'task_id': 'mining-task-id',
                    'timestamp': '1624376173',
                    'model': {
                        'model_hash': 'abc123',
                        'mean_average_precision': 0.5,
                        'context': 'fake_context'
                    }
                }
            },
            'head_task_id': 'mining-task-id',
        }
        pb_format.ParseDict(dict_tasks, mir_tasks)

        return (mir_metadatas, mir_annotations, mir_keywords, mir_tasks, mir_context)

    # protected: check result
    def _check_keywords(self, expected_mir_keywords: mirpb.MirKeywords, actual_mir_keywords: mirpb.MirKeywords) -> None:
        """
        for mir_keywords, both keyids and asset_ids should be compared as set
        """
        self.assertEqual(expected_mir_keywords.keywords.keys(), actual_mir_keywords.keywords.keys())
        logging.info(f"expected: {expected_mir_keywords.index_predifined_keyids.keys()}")
        logging.info(f"actual: {actual_mir_keywords.index_predifined_keyids.keys()}")
        self.assertEqual(expected_mir_keywords.index_predifined_keyids.keys(),
                         actual_mir_keywords.index_predifined_keyids.keys())
        for k, v in actual_mir_keywords.keywords.items():
            self.assertEqual(set(v.predifined_keyids), set(expected_mir_keywords.keywords[k].predifined_keyids))
        for k, v in actual_mir_keywords.index_predifined_keyids.items():
            self.assertEqual(set(v.asset_ids), set(expected_mir_keywords.index_predifined_keyids[k].asset_ids))

    # public: test cases
    def test_normal_00(self):
        """
        normal cases: no project context, commit twice
        """
        mir_metadatas, mir_annotations, mir_keywords, mir_tasks, mir_context = self._prepare_mir_pb(with_project=False)
        mir_datas_expect = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
            mirpb.MirStorage.MIR_TASKS: mir_tasks,
        }
        mir_storage_list = [
            mirpb.MirStorage.MIR_METADATAS,
            mirpb.MirStorage.MIR_ANNOTATIONS,
            mirpb.MirStorage.MIR_TASKS,
        ]
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      task_id='mining-task-id',
                                                      his_branch='master',
                                                      mir_datas=mir_datas_expect,
                                                      commit_message='test_ops')
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms_list=mir_storage_list,
            as_dict=False,
        )
        actual_data = dict(zip(mir_storage_list, mir_datas))
        print(f"actual_data: {actual_data}")
        print(f"mir_datas_expect: {mir_datas_expect}")
        self.assertDictEqual(actual_data, mir_datas_expect)
        loaded_mir_keywords = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                                mir_branch='a',
                                                                                ms=mirpb.MirStorage.MIR_KEYWORDS,
                                                                                mir_task_id='mining-task-id',
                                                                                as_dict=False)
        self._check_keywords(expected_mir_keywords=mir_keywords, actual_mir_keywords=loaded_mir_keywords)
        loaded_mir_context = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                               mir_branch='a',
                                                                               ms=mirpb.MirStorage.MIR_CONTEXT,
                                                                               mir_task_id='mining-task-id',
                                                                               as_dict=False)
        try:
            self.assertEqual(loaded_mir_context, mir_context)
        except AssertionError as e:
            logging.info(f"expected: {mir_context}")
            logging.info(f"actual: {loaded_mir_context}")
            raise e

        # add another commit a@t2, which has empty dataset
        mir_tasks_2 = mirpb.MirTasks()
        mir_storage_ops.update_mir_tasks(mir_tasks=mir_tasks_2,
                                         task_type=mirpb.TaskType.TaskTypeMining,
                                         task_id='t2',
                                         message='task-t2')
        mir_datas_expect_2 = [mirpb.MirMetadatas(), mirpb.MirAnnotations(), mir_tasks_2]
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      task_id='t2',
                                                      his_branch='a',
                                                      mir_datas=mir_datas_expect_2,
                                                      commit_message='t2')
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms_list=mir_storage_list,
            as_dict=False,
        )
        self.assertDictEqual(mir_datas, mir_datas_expect)
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='t2',
            mir_storages=mir_storage_list,
            as_dict=False,
        )
        self.assertDictEqual(mir_datas, mir_datas_expect_2)

        # load_single_model: have model
        actual_dict_model = mir_storage_ops.MirStorageOps.load_single_model(mir_root=self._mir_root,
                                                                            mir_branch='a',
                                                                            mir_task_id='mining-task-id')
        self.assertEqual(
            actual_dict_model, {
                'model_hash': 'abc123',
                'mean_average_precision': 0.5,
                'context': 'fake_context',
                'executor_config': {},
                'task_parameters': ''
            })
        # load_single_model: have no model
        with self.assertRaises(MirError):
            mir_storage_ops.MirStorageOps.load_single_model(mir_root=self._mir_root, mir_branch='a', mir_task_id='t2')

    def test_normal_01(self):
        # change project settings
        context.save(mir_root=self._mir_root, project_class_ids=[3, 4])

        mir_metadatas, mir_annotations, mir_keywords, mir_tasks, mir_context = self._prepare_mir_pb(with_project=True)

        mir_datas_expect = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
            mirpb.MirStorage.MIR_TASKS: mir_tasks,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      task_id='mining-task-id',
                                                      his_branch='master',
                                                      mir_datas=mir_datas_expect,
                                                      commit_message='test_ops')
        loaded_mir_keywords = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                                mir_branch='a',
                                                                                ms=mirpb.MirStorage.MIR_KEYWORDS,
                                                                                mir_task_id='mining-task-id',
                                                                                as_dict=False)
        self._check_keywords(expected_mir_keywords=mir_keywords, actual_mir_keywords=loaded_mir_keywords)
        loaded_mir_context = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                               mir_branch='a',
                                                                               ms=mirpb.MirStorage.MIR_CONTEXT,
                                                                               mir_task_id='mining-task-id',
                                                                               as_dict=False)
        try:
            self.assertEqual(loaded_mir_context, mir_context)
        except AssertionError as e:
            logging.info(f"expected: {mir_context}")
            logging.info(f"actual: {loaded_mir_context}")
            raise e
