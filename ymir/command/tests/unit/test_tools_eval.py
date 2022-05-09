from collections import Counter
import json
import os
import shutil
import unittest

from google.protobuf import json_format
import numpy as np
from pycocotools import coco, cocoeval

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
        self._coco_a = os.path.join(self._test_root, 'coco_a.json')
        self._coco_b = os.path.join(self._test_root, 'coco_b.json')

    def setUp(self) -> None:
        self._prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['person', 'cat', 'tv', 'dog'])
        self._prepare_mir_repo()
        self._prepare_coco()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._working_root)
        test_utils.remake_dirs(self._mir_root)

    def _prepare_coco(self) -> None:
        self._prepare_coco_a()
        self._prepare_coco_b()

    def _prepare_coco_a(self) -> None:
        coco_dict = {
            "info": {},
            "licenses": [
                {
                    "id": 1,
                    "name": "Attribution-NonCommercial-ShareAlike License",
                    "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/",
                },
            ],
            "categories": [
                {
                    "id": 0,
                    "name": "person",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                }, {
                    "id": 1,
                    "name": "cat",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                }, {
                    "id": 2,
                    "name": "tv",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                },
            ],
            "images": [
                {
                    "id": 1,
                    "license": 1,
                    "file_name": "a0",
                    "height": 500,
                    "width": 500,
                }, {
                    "id": 2,
                    "license": 1,
                    "file_name": "a1",
                    "height": 500,
                    "width": 500,
                }, {
                    "id": 3,
                    "license": 1,
                    "file_name": "a2",
                    "height": 500,
                    "width": 500,
                },
            ],
            "annotations": [
                {
                    "id": 1,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [50, 50, 50, 50],
                    "score": 1,
                    "area": 2500,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 2,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [150, 50, 75, 75],
                    "score": 1,
                    "area": 5625,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 3,
                    "image_id": 1,
                    "category_id": 1,
                    "bbox": [150, 150, 75, 75],
                    "score": 1,
                    "area": 5625,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 4,
                    "image_id": 1,
                    "category_id": 2,
                    "bbox": [350, 50, 100, 100],
                    "score": 1,
                    "area": 10000,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 5,
                    "image_id": 2,
                    "category_id": 2,
                    "bbox": [300, 300, 100, 100],
                    "score": 1,
                    "area": 10000,
                    "segmentation": [],
                    "iscrowd": 0
                },
            ]
        }
        with open(self._coco_a, 'w') as f:
            f.write(json.dumps(coco_dict))

    def _prepare_coco_b(self) -> None:
        coco_dict = {
            "info": {},
            "licenses": [
                {
                    "id": 1,
                    "name": "Attribution-NonCommercial-ShareAlike License",
                    "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/",
                },
            ],
            "categories": [
                {
                    "id": 0,
                    "name": "person",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                }, {
                    "id": 1,
                    "name": "cat",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                }, {
                    "id": 2,
                    "name": "tv",
                    "supercategory": "unknown",
                    "keypoints": [],
                    "skeleton": []
                },
            ],
            "images": [
                {
                    "id": 1,
                    "license": 1,
                    "file_name": "a0",
                    "height": 500,
                    "width": 500,
                }, {
                    "id": 2,
                    "license": 1,
                    "file_name": "a1",
                    "height": 500,
                    "width": 500,
                }, {
                    "id": 3,
                    "license": 1,
                    "file_name": "a2",
                    "height": 500,
                    "width": 500,
                },
            ],
            "annotations": [
                {
                    "id": 1,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [45, 45, 52, 52],
                    "score": 0.7,
                    "area": 2704,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 2,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [150, 50, 73, 73],
                    "score": 0.8,
                    "area": 5329,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 3,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [350, 50, 76, 76],
                    "score": 0.9,
                    "area": 5776,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 4,
                    "image_id": 1,
                    "category_id": 1,
                    "bbox": [150, 160, 78, 78],
                    "score": 0.9,
                    "area": 6084,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 5,
                    "image_id": 1,
                    "category_id": 2,
                    "bbox": [350, 50, 102, 103],
                    "score": 0.9,
                    "area": 10506,
                    "segmentation": [],
                    "iscrowd": 0
                }, {
                    "id": 6,
                    "image_id": 2,
                    "category_id": 2,
                    "bbox": [300, 300, 103, 110],
                    "score": 0.9,
                    "area": 11330,
                    "segmentation": [],
                    "iscrowd": 0
                },
            ]
        }
        with open(self._coco_b, 'w') as f:
            f.write(json.dumps(coco_dict))

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

        annotations_list = mir_coco.get_annotations(conf_thr=2)
        self.assertEqual(0, len(annotations_list))

    def test_mir_eval_00(self):
        """ align our eval with original COCOeval """

        # original eval from pycocotools
        coco_gt = coco.COCO(self._coco_a)
        coco_dt = coco.COCO(self._coco_a)
        coco_evaluator = cocoeval.COCOeval(cocoGt=coco_gt, cocoDt=coco_dt, iouType='bbox')
        coco_evaluator.evaluate()
        coco_evaluator.accumulate()
        coco_evaluator.summarize()

        # ymir's eval
        mir_gt = eval.MirCoco(mir_root=self._mir_root, rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=False))
        mir_dt = eval.MirCoco(mir_root=self._mir_root, rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=False))
        mir_evaluator = eval.MirEval(coco_gt=mir_gt, coco_dt=mir_dt)
        mir_evaluator.evaluate()
        mir_evaluator.accumulate()

        mir_evaluator.summarize()
        self.assertTrue(np.array_equal(coco_evaluator.stats, mir_evaluator.stats))

        mir_evaluation_result = mir_evaluator.get_evaluation_result()
        breakpoint()
