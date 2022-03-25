import logging
import os
import shutil
from typing import Type
import unittest
import zlib

import google.protobuf.json_format as pb_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import exodus, mir_storage_ops
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
import tests.utils as test_utils


class TestExodus(unittest.TestCase):
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
        self._test_open_normal_cases("metadatas.mir", "a", mirpb.MirMetadatas)
        self._test_open_normal_cases("tasks.mir", "a", mirpb.MirTasks)
        self._test_open_normal_cases("annotations.mir", "a", mirpb.MirAnnotations)
        self._test_open_normal_cases("keywords.mir", "a", mirpb.MirKeywords)

    def test_open_abnormal_cases(self):
        # wrong branches
        self._test_open_abnormal_cases("fake-file", "fake-branch", MirCode.RC_CMD_INVALID_BRANCH_OR_TAG)
        # wrong file names
        self._test_open_abnormal_cases("fake-file", "coco-2017-train", MirCode.RC_CMD_INVALID_MIR_REPO)
        # empty args
        self._test_open_abnormal_cases("fake-file", "", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases("", "fake-branch", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases("", "", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases("fake-file", None, MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases(None, "fake-branch", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases(None, None, MirCode.RC_CMD_INVALID_ARGS)

    # protected: test cases
    def _test_open_normal_cases(self, file_name: str, branch: str, pb_class: Type):
        contents = exodus.read_mir(mir_root=self._mir_root, rev=branch, file_name=file_name)
        pb_instance = pb_class()
        pb_instance.ParseFromString(contents)

    def _test_open_abnormal_cases(self, file_name: str, branch: str, expected_code: int):
        actual_exception = None
        try:
            exodus.read_mir(mir_root=self._mir_root, rev=branch, file_name=file_name)
        except (TypeError, ValueError) as e:
            actual_exception = e
        except MirRuntimeError as e:
            actual_exception = e
            self.assertIsInstance(actual_exception, MirRuntimeError)
            self.assertEqual(actual_exception.error_code, expected_code)
        except FileNotFoundError as e:
            actual_exception = e
            self.assertIsInstance(actual_exception, FileNotFoundError)
        finally:
            self.assertIsNotNone(actual_exception)

    # protected: misc
    def _prepare_dir(self):
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        os.makedirs(self._mir_root, exist_ok=True)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)
        test_utils.mir_repo_create_branch(self._mir_root, "a")

        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()

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

        mir_datas = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeMining,
                                           task_id='mining-task-id',
                                           message='branch_a_for_test_exodus')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas=mir_datas,
                                                      task=task)

        test_utils.mir_repo_checkout(self._mir_root, "master")
