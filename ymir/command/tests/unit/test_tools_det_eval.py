import os
import shutil
import unittest

from google.protobuf import json_format
import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import det_eval_coco, det_eval_utils, det_eval_voc, mir_storage_ops
from tests import utils as test_utils


class TestToolsDetEval(unittest.TestCase):
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
            'prediction': {
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
                },
            },
            'head_task_id': 'a',
            'image_cks': {
                'a0': {
                    'cks': {
                        'weather': 'sunny',
                        'color': 'red',
                    },
                },
                'a1': {
                    'cks': {
                        'weather': 'sunny',
                        'color': 'blue',
                    },
                },
            },
            'ground_truth': {
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

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # public: test cases
    def test_mir_coco(self):
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_keywords: mirpb.MirKeywords
        mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='a',
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])
        mir_coco = det_eval_utils.MirDataset(asset_ids=mir_metadatas.attributes.keys(),
                                             pred_or_gt_annotations=mir_annotations.ground_truth,
                                             class_ids=mir_keywords.gt_idx.cis.keys(),
                                             conf_thr=None,
                                             dataset_id='a@a')
        self.assertEqual(['a0', 'a1', 'a2'], mir_coco.get_asset_ids())
        self.assertEqual([0, 1, 2], mir_coco.get_asset_idxes())
        self.assertEqual([0, 1, 2], mir_coco.get_class_ids())

        self.assertEqual(2, len(mir_coco.img_cat_to_annotations[(0, 0)]))

    def test_det_eval_coco_00(self):
        """ align our eval with original COCOeval """

        # original result from pycocotools
        expected_stats = np.array([0.61177118, 0.88888889, 0.41749175])

        # ymir's eval
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_keywords: mirpb.MirKeywords
        mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='a',
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])

        mir_gt = det_eval_utils.MirDataset(asset_ids=mir_metadatas.attributes.keys(),
                                           pred_or_gt_annotations=mir_annotations.ground_truth,
                                           class_ids=mir_keywords.gt_idx.cis.keys(),
                                           conf_thr=None,
                                           dataset_id='a')
        mir_dt = det_eval_utils.MirDataset(asset_ids=mir_metadatas.attributes.keys(),
                                           pred_or_gt_annotations=mir_annotations.prediction,
                                           class_ids=mir_keywords.pred_idx.cis.keys(),
                                           conf_thr=0,
                                           dataset_id='a')

        params = det_eval_coco.Params()
        params.catIds = mir_gt.get_class_ids()
        mir_evaluator = det_eval_coco.CocoDetEval(coco_gt=mir_gt, coco_dt=mir_dt, params=params)
        mir_evaluator.evaluate()
        mir_evaluator.accumulate()
        mir_evaluator.summarize()
        self.assertTrue(np.isclose(expected_stats, mir_evaluator.stats).all())

        single_dataset_evaluation = mir_evaluator.get_evaluation_result(area_ranges_index=0, max_dets_index=0)
        self.assertTrue(len(single_dataset_evaluation.iou_evaluations) > 0)
        
    def test_det_eval_voc_00(self) -> None:
        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        mir_keywords: mirpb.MirKeywords
        mir_metadatas, mir_annotations, mir_keywords = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='a',
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS, mirpb.MirStorage.MIR_KEYWORDS])

        mir_gt = det_eval_utils.MirDataset(asset_ids=mir_metadatas.attributes.keys(),
                                           pred_or_gt_annotations=mir_annotations.ground_truth,
                                           class_ids=mir_keywords.gt_idx.cis.keys(),
                                           conf_thr=None,
                                           dataset_id='a')
        mir_dt = det_eval_utils.MirDataset(asset_ids=mir_metadatas.attributes.keys(),
                                           pred_or_gt_annotations=mir_annotations.prediction,
                                           class_ids=mir_keywords.pred_idx.cis.keys(),
                                           conf_thr=0,
                                           dataset_id='a')

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0.0005
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.need_pr_curve = True
        evaluate_config.gt_dataset_id = 'a'
        evaluate_config.pred_dataset_ids.append('a')
        evaluate_config.class_ids[:] = [0, 1]
        evaluation = det_eval_voc.det_evaluate(mir_dts=[mir_dt],
                                               mir_gt=mir_gt,
                                               config=evaluate_config)
        self.assertTrue(len(evaluation.dataset_evaluations) == 1)
