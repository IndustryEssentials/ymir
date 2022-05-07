from collections import Counter
import logging
import os
import shutil
import unittest

from google.protobuf import json_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import eval, mir_storage_ops, revs_parser
from tests import utils as test_utils

class TestToolsEval(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._working_root = os.path.join(self._test_root, 'work')
        self._mir_root = os.path.join(self._test_root, 'mir-root')

    def setUp(self) -> None:
        self._prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['person', 'cat', 'tv', 'dog'])
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
        """ branch a: a ground truth branch """
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
        """ branch b: a prediction / detection branch """
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
                                    'x': 45,
                                    'y': 45,
                                    'w': 52,
                                    'h': 52,
                                },
                                'class_id': 0,
                                'score': 0.7,
                            }, {
                                'index': 1,
                                'box': {
                                    'x': 150,
                                    'y': 50,
                                    'w': 73,
                                    'h': 73,
                                },
                                'class_id': 0,
                                'score': 0.8,
                            }, {
                                'index': 2,
                                'box': {
                                    'x': 350,
                                    'y': 50,
                                    'w': 76,
                                    'h': 76,
                                },
                                'class_id': 0,
                                'score': 0.9,
                            }, {
                                'index': 3,
                                'box': {
                                    'x': 150,
                                    'y': 160,
                                    'w': 78,
                                    'h': 78,
                                },
                                'class_id': 1,
                                'score': 0.9,
                            }, {
                                'index': 4,
                                'box': {
                                    'x': 350,
                                    'y': 50,
                                    'w': 102,
                                    'h': 103,
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
                                    'w': 103,
                                    'h': 110,
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
    def test_mir_coco(self):
        mir_coco = eval.MirCoco(mir_root=self._mir_root, rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=False))
        self.assertEqual(['a0', 'a1', 'a2'], mir_coco.get_asset_ids())
        self.assertEqual([0, 1, 2], mir_coco.get_asset_idxes())
        self.assertEqual([0, 1, 2], mir_coco.get_class_ids())

        # get annotations
        annotations_list = mir_coco.get_annotations()
        counter = Counter([elem['asset_idx'] for elem in annotations_list])
        self.assertEqual(4, counter[0])
        self.assertEqual(1, counter[1])

        annotations_list = mir_coco.get_annotations(asset_idxes=[0, 2])
        counter = Counter([elem['asset_idx'] for elem in annotations_list])
        self.assertEqual(4, counter[0])
        self.assertEqual(0, counter[2])

        annotations_list = mir_coco.get_annotations(asset_idxes=[0, 1], class_ids=[0, 3])
        counter = Counter([elem['asset_idx'] for elem in annotations_list])
        self.assertEqual(2, counter[0])
        self.assertEqual(0, counter[1])

    def test_mir_eval_00(self):
        coco_gt = eval.MirCoco(mir_root=self._mir_root, rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=False))
        coco_dt = eval.MirCoco(mir_root=self._mir_root, rev_tid=revs_parser.parse_single_arg_rev('b@b', need_tid=False))
        evaluator = eval.MirEval(coco_gt=coco_gt, coco_dt=coco_dt)
        evaluator.evaluate()
        evaluator.accumulate()
        evaluator.summarize()
        breakpoint()
        logging.info(f"evaluator stats: {evaluator.stats}")
        raise ValueError('a fake error occured')  # for test: captured outputs
