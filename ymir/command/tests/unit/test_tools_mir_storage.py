import os
import shutil
import unittest

import google.protobuf.json_format as pb_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops
from tests import utils as test_utils


class TestMirStorage(unittest.TestCase):
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

    # public: test cases
    def test_open_normal_cases(self):

        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_tasks = mirpb.MirTasks()

        dict_metadatas = {
            'attributes': {
                'd4e4a60147f1e35bc7f5bc89284aa16073b043c9': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                }
            }
        }
        pb_format.ParseDict(dict_metadatas, mir_metadatas)

        dict_annotations = {
            "task_annotations": {
                "5928508c-1bc0-43dc-a094-0352079e39b5": {
                    "image_annotations": {
                        "d4e4a60147f1e35bc7f5bc89284aa16073b043c9": {
                            'annotations': [{
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 50
                                },
                                'classId': 2
                            }]
                        }
                    }
                }
            }
        }

        pb_format.ParseDict(dict_annotations, mir_annotations)

        dict_keywords = {
            'keywords': {
                'd4e4a60147f1e35bc7f5bc89284aa16073b043c9': {
                    'predifined_keyids': [1],
                    'customized_keywords': ['abc']
                }
            },
            'predifined_keyids_cnt': {
                1: 1
            },
            'predifined_keyids_total': 1,
            'customized_keywords_cnt': {
                'abc': 1
            },
            'customized_keywords_total': 1
        }
        pb_format.ParseDict(dict_keywords, mir_keywords)

        dict_tasks = {
            'tasks': {
                '5928508c-1bc0-43dc-a094-0352079e39b5': {
                    'type': 'TaskTypeMining',
                    'name': 'mining',
                    'task_id': 'mining-task-id',
                    'timestamp': '1624376173'
                }
            }
        }
        pb_format.ParseDict(dict_tasks, mir_tasks)

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
        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=self._mir_root,
                                                       mir_branch='a',
                                                       mir_task_id='mining-task-id',
                                                       mir_storages=[x for x in mir_datas_expect.keys()])
        self.assertDictEqual(mir_datas, mir_datas_expect)

        # add another commit a@t2, which has empty dataset
        mir_datas_expect_2 = {
            mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas(),
            mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations(),
            mirpb.MirStorage.MIR_TASKS: mirpb.MirTasks(),
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      task_id='t2',
                                                      his_branch='a',
                                                      mir_datas=mir_datas_expect_2,
                                                      commit_message='t2')
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=self._mir_root,
                                                       mir_branch='a',
                                                       mir_task_id='mining-task-id',
                                                       mir_storages=[x for x in mir_datas_expect.keys()])
        self.assertDictEqual(mir_datas, mir_datas_expect)
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=self._mir_root,
                                                       mir_branch='a',
                                                       mir_task_id='t2',
                                                       mir_storages=[x for x in mir_datas_expect.keys()])
        self.assertDictEqual(mir_datas, mir_datas_expect_2)

    # protected: misc
    def _prepare_dir(self):
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        os.makedirs(self._mir_root, exist_ok=True)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)
