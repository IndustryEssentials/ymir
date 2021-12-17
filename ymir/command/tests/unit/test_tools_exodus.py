import os
import shutil
import unittest

import google.protobuf.json_format as pb_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import exodus
from mir.tools.code import MirCode
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
        self._test_open_normal_cases("metadatas.mir", "a")
        self._test_open_normal_cases("tasks.mir", "a")
        self._test_open_normal_cases("annotations.mir", "a")
        self._test_open_normal_cases("keywords.mir", "a")

    def test_open_abnormal_cases(self):
        # wrong branches
        self._test_open_abnormal_cases("fake-file", "fake-branch", MirCode.RC_CMD_INVALID_BRANCH_OR_TAG)
        # wrong file names
        self._test_open_abnormal_cases("fake-file", "coco-2017-train", MirCode.RC_CMD_INVALID_MIR_FILE)
        # empty args
        self._test_open_abnormal_cases("fake-file", "", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases("", "fake-branch")
        self._test_open_abnormal_cases("", "", MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases("fake-file", None, MirCode.RC_CMD_INVALID_ARGS)
        self._test_open_abnormal_cases(None, "fake-branch")
        self._test_open_abnormal_cases(None, None, MirCode.RC_CMD_INVALID_ARGS)

    # protected: test cases
    def _test_open_normal_cases(self, file_name: str, branch: str):
        with exodus.open_mir(mir_root=self._mir_root, file_name=file_name, rev=branch, mode="rb") as f:
            self.assertIsNotNone(f)
            contents = f.read()
            self.assertNotEqual(len(contents), 0)

    def _test_open_abnormal_cases(self, file_name: str, branch: str, expected_code=0):
        actual_exception = None
        try:
            with exodus.open_mir(mir_root=self._mir_root, file_name=file_name, rev=branch, mode="rb"):
                pass
        except (TypeError, ValueError) as e:
            actual_exception = e
        except exodus.ExodusError as e:
            actual_exception = e
            self.assertIsInstance(actual_exception, exodus.ExodusError)
            self.assertEqual(actual_exception.code, expected_code)
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
                    'customized_keywords': ["abc"]
                }
            }
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

        test_utils.mir_repo_commit_all(mir_root=self._mir_root,
                                       mir_metadatas=mir_metadatas,
                                       mir_annotations=mir_annotations,
                                       mir_tasks=mir_tasks,
                                       src_branch='master',
                                       dst_branch='a',
                                       task_id='5928508c-1bc0-43dc-a094-0352079e39b5',
                                       no_space_message="branch_a_for_test_exodus")

        test_utils.mir_repo_checkout(self._mir_root, "master")
