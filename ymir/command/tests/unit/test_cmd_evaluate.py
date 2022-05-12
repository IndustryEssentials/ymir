import os
import shutil
import unittest

from google.protobuf import json_format

from mir.commands import evaluate
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdEvaluate(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._working_root = os.path.join(self._test_root, 'work')
        self._mir_root = os.path.join(self._test_root, 'mir-root')

    def setUp(self) -> None:
        self._prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['person', 'cat', 'tv'])
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._working_root)
        test_utils.remake_dirs(self._mir_root)

    def _prepare_mir_repo(self) -> None:
        test_utils.mir_repo_init(self._mir_root)
        self._prepare_mir_repo_branch_a()
        self._prepare_mir_repo_branch_b()

    def _prepare_mir_repo_branch_a(self) -> None:
        metadatas_dict = {
            'attributes': {
                'a0': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                },
                'a1': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                },
                'a2': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                }
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        annotations_dict = {
            'task_annotations': {
                'a': {
                    'image_annotations': {
                        'a0': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 50,
                                    'y': 50,
                                    'w': 50,
                                    'h': 50,
                                },
                                'class_id': 0,
                                'score': 1,
                            }, {
                                'index': 1,
                                'box': {
                                    'x': 150,
                                    'y': 50,
                                    'w': 75,
                                    'h': 75,
                                },
                                'class_id': 0,
                                'score': 1,
                            }, {
                                'index': 2,
                                'box': {
                                    'x': 150,
                                    'y': 150,
                                    'w': 75,
                                    'h': 75,
                                },
                                'class_id': 1,
                                'score': 1,
                            }, {
                                'index': 3,
                                'box': {
                                    'x': 350,
                                    'y': 50,
                                    'w': 100,
                                    'h': 100,
                                },
                                'class_id': 2,
                                'score': 1,
                            }]
                        },
                        'a1': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 300,
                                    'y': 300,
                                    'w': 100,
                                    'h': 100,
                                },
                                'class_id': 2,
                                'score': 1,
                            }]
                        },
                    }
                }
            },
            'head_task_id': 'a'
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='a', message='import')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    def _prepare_mir_repo_branch_b(self) -> None:
        metadatas_dict = {
            'attributes': {
                'a0': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                },
                'a1': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                },
                'a2': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeUnknown',
                    'width': 500,
                    'height': 500,
                    'imageChannels': 3
                }
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        annotations_dict = {
            'task_annotations': {
                'b': {
                    'image_annotations': {
                        'a0': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 50,
                                    'y': 50,
                                    'w': 50,
                                    'h': 50,
                                },
                                'class_id': 0,
                                'score': 0.7,
                            }, {
                                'index': 1,
                                'box': {
                                    'x': 150,
                                    'y': 50,
                                    'w': 75,
                                    'h': 75,
                                },
                                'class_id': 0,
                                'score': 0.8,
                            }, {
                                'index': 2,
                                'box': {
                                    'x': 150,
                                    'y': 150,
                                    'w': 75,
                                    'h': 75,
                                },
                                'class_id': 1,
                                'score': 0.9,
                            }, {
                                'index': 3,
                                'box': {
                                    'x': 350,
                                    'y': 50,
                                    'w': 100,
                                    'h': 100,
                                },
                                'class_id': 2,
                                'score': 0.9,
                            }]
                        },
                        'a1': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 300,
                                    'y': 300,
                                    'w': 100,
                                    'h': 100,
                                },
                                'class_id': 2,
                                'score': 0.9,
                            }]
                        },
                    }
                }
            },
            'head_task_id': 'b'
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='b', message='import')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='b',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # public: test cases
    def test_00(self) -> None:
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.work_dir = self._working_root
        fake_args.src_revs = 'a;b'
        fake_args.gt_rev = 'b'
        fake_args.dst_rev = 'c@c'
        fake_args.conf_thr = 0.3
        fake_args.iou_thrs = '0.5:0.95:0.05'
        fake_args.need_pr_curve = False
        evaluate_instance = evaluate.CmdEvaluate(fake_args)
        return_code = evaluate_instance.run()

        self.assertEqual(return_code, MirCode.RC_OK)

        # check evaluation result
        mir_tasks: mirpb.MirTasks = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                                      mir_branch='c',
                                                                                      mir_task_id='c',
                                                                                      ms=mirpb.MirStorage.MIR_TASKS)
        evaluation_result = mir_tasks.tasks[mir_tasks.head_task_id].evaluation
        self.assertEqual({'a', 'b'}, set(evaluation_result.dataset_evaluations.keys()))
