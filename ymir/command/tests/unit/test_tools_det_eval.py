import os
import shutil
from typing import Any
import unittest

from google.protobuf import json_format
import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, revs_parser
from mir.tools.eval import eval_ctl_ops, det_eval_voc
from tests import utils as test_utils


class TestToolsDetEval(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.maxDiff = None
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
                'type': mirpb.ObjectType.OT_DET_BOX,
                'image_annotations': {
                    'a0': {
                        'boxes': [{
                            'index': 0,
                            'box': {
                                'x': 45,
                                'y': 45,
                                'w': 52,
                                'h': 52,
                            },
                            'class_id': 0,
                            'polygon': [],
                            'score': 0.7,
                        }, {
                            'index': 1,
                            'box': {
                                'x': 150,
                                'y': 50,
                                'w': 73,
                                'h': 73,
                            },
                            'polygon': [],
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
                            'polygon': [],
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
                            'polygon': [],
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
                            'polygon': [],
                            'score': 0.9,
                        }, {
                            'index': 5,
                            'box': {
                                'x': 350,
                                'y': 50,
                                'w': 102,
                                'h': 103,
                            },
                            'class_id': 3,
                            'polygon': [],
                            'score': 0.9,
                        }],
                        'img_class_ids': [0, 1, 2, 3],
                    },
                    'a1': {
                        'boxes': [{
                            'index': 0,
                            'box': {
                                'x': 300,
                                'y': 300,
                                'w': 103,
                                'h': 110,
                            },
                            'polygon': [],
                            'class_id': 2,
                            'score': 0.9,
                        }],
                        'img_class_ids': [2],
                    },
                },
                'eval_class_ids': [0, 1, 2, 3],
                'task_class_ids': [0, 1, 2, 3],
            },
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
                'type': mirpb.ObjectType.OT_DET_BOX,
                'image_annotations': {
                    'a0': {
                        'boxes': [{
                            'index': 0,
                            'box': {
                                'x': 50,
                                'y': 50,
                                'w': 50,
                                'h': 50,
                            },
                            'polygon': [],
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
                            'polygon': [],
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
                            'polygon': [],
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
                            'polygon': [],
                            'class_id': 2,
                            'score': 1,
                        }],
                        'img_class_ids': [0, 1, 2],
                    },
                    'a1': {
                        'boxes': [{
                            'index': 0,
                            'box': {
                                'x': 300,
                                'y': 300,
                                'w': 100,
                                'h': 100,
                            },
                            'polygon': [],
                            'class_id': 2,
                            'score': 1,
                        }],
                        'img_class_ids': [2],
                    },
                },
                'task_class_ids': [0, 1, 2],
            }
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        task = mir_storage_ops.create_task_record(task_type=mirpb.TaskType.TaskTypeImportData, task_id='a', message='import')
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

    # private: check result
    def _check_fpfn(self, actual_mir_annotations: mirpb.MirAnnotations) -> None:
        expected_annotations_dict = {
            'ground_truth': {
                'image_annotations': {
                    'a0': {
                        'boxes': [{
                            'box': {
                                'x': 50,
                                'y': 50,
                                'w': 50,
                                'h': 50,
                                'rotate_angle': 0.0
                            },
                            'score': 1.0,
                            'cm': 'MTP',
                            'index': 0,
                            'class_id': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'polygon': [],
                            'det_link_id': 0,
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 1,
                            'box': {
                                'x': 150,
                                'y': 50,
                                'w': 75,
                                'h': 75,
                                'rotate_angle': 0.0
                            },
                            'score': 1.0,
                            'polygon': [],
                            'cm': 'MTP',
                            'det_link_id': 1,
                            'class_id': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 2,
                            'box': {
                                'x': 150,
                                'y': 150,
                                'w': 75,
                                'h': 75,
                                'rotate_angle': 0.0
                            },
                            'class_id': 1,
                            'score': 1.0,
                            'cm': 'MTP',
                            'det_link_id': 3,
                            'polygon': [],
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 3,
                            'box': {
                                'x': 350,
                                'y': 50,
                                'w': 100,
                                'h': 100,
                                'rotate_angle': 0.0
                            },
                            'class_id': 2,
                            'score': 1.0,
                            'cm': 'IGNORED',
                            'det_link_id': -1,
                            'polygon': [],
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }],
                        'img_class_ids': [0, 1, 2],
                    },
                    'a1': {
                        'boxes': [{
                            'box': {
                                'x': 300,
                                'y': 300,
                                'w': 100,
                                'h': 100,
                                'rotate_angle': 0.0
                            },
                            'class_id': 2,
                            'score': 1.0,
                            'cm': 'IGNORED',
                            'det_link_id': -1,
                            'polygon': [],
                            'index': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }],
                        'img_class_ids': [2],
                    },
                },
                'is_instance_segmentation': False,
                'task_class_ids': [0, 1, 2],
                'task_id': 'a',
                'eval_class_ids': [],
                'executor_config': '',
                'type': 'OT_DET_BOX',
            },
            'prediction': {
                'image_annotations': {
                    'a1': {
                        'boxes': [{
                            'box': {
                                'x': 300,
                                'y': 300,
                                'w': 103,
                                'h': 110,
                                'rotate_angle': 0.0
                            },
                            'class_id': 2,
                            'score': 0.9,
                            'cm': 'IGNORED',
                            'polygon': [],
                            'det_link_id': -1,
                            'index': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }],
                        'img_class_ids': [2],
                    },
                    'a0': {
                        'boxes': [{
                            'box': {
                                'x': 45,
                                'y': 45,
                                'w': 52,
                                'h': 52,
                                'rotate_angle': 0.0
                            },
                            'score': 0.7,
                            'cm': 'TP',
                            'index': 0,
                            'polygon': [],
                            'class_id': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'det_link_id': 0,
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 1,
                            'box': {
                                'x': 150,
                                'y': 50,
                                'w': 73,
                                'h': 73,
                                'rotate_angle': 0.0
                            },
                            'score': 0.8,
                            'cm': 'TP',
                            'det_link_id': 1,
                            'polygon': [],
                            'class_id': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 2,
                            'box': {
                                'x': 350,
                                'y': 50,
                                'w': 76,
                                'h': 76,
                                'rotate_angle': 0.0
                            },
                            'score': 0.9,
                            'cm': 'FP',
                            'det_link_id': -1,
                            'polygon': [],
                            'class_id': 0,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 3,
                            'box': {
                                'x': 150,
                                'y': 160,
                                'w': 78,
                                'h': 78,
                                'rotate_angle': 0.0
                            },
                            'class_id': 1,
                            'score': 0.9,
                            'cm': 'TP',
                            'polygon': [],
                            'det_link_id': 2,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 4,
                            'box': {
                                'x': 350,
                                'y': 50,
                                'w': 102,
                                'h': 103,
                                'rotate_angle': 0.0
                            },
                            'class_id': 2,
                            'score': 0.9,
                            'polygon': [],
                            'cm': 'IGNORED',
                            'det_link_id': -1,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }, {
                            'index': 5,
                            'box': {
                                'x': 350,
                                'y': 50,
                                'w': 102,
                                'h': 103,
                                'rotate_angle': 0.0
                            },
                            'class_id': 3,
                            'score': 0.9,
                            'polygon': [],
                            'cm': 'IGNORED',
                            'det_link_id': -1,
                            'anno_quality': 0.0,
                            'tags': {},
                            'class_name': '',
                            'type': 'OST_NOTSET',
                            'iscrowd': 0,
                            'mask': '',
                            'mask_area': 0,
                        }],
                        'img_class_ids': [0, 1, 2, 3],
                    }
                },
                'is_instance_segmentation': False,
                'task_id': 'a',
                'eval_class_ids': [0, 1, 2, 3],
                'executor_config': '',
                'type': 'OT_DET_BOX',
                'task_class_ids': [0, 1, 2, 3],
            },
            'image_cks': {
                'a1': {
                    'cks': {
                        'color': 'blue',
                        'weather': 'sunny'
                    },
                    'image_quality': 0.0
                },
                'a0': {
                    'cks': {
                        'color': 'red',
                        'weather': 'sunny'
                    },
                    'image_quality': 0.0
                }
            }
        }
        actual_annotations_dict = json_format.MessageToDict(actual_mir_annotations,
                                                            including_default_value_fields=True,
                                                            preserving_proto_field_name=True)
        self.assertEqual(expected_annotations_dict, actual_annotations_dict)

    # public: test cases
    def test_det_eval_voc_00(self) -> None:
        mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=self._mir_root, mir_branch='a', mir_task_id='a', ms=mirpb.MirStorage.MIR_ANNOTATIONS)

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0.0005
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.need_pr_curve = True
        evaluate_config.class_ids[:] = [0, 1]
        evaluation: mirpb.Evaluation = det_eval_voc.evaluate(prediction=mir_annotations.prediction,
                                                             ground_truth=mir_annotations.ground_truth,
                                                             config=evaluate_config)
        self._check_fpfn(mir_annotations)
        sde = evaluation.dataset_evaluation
        see = sde.iou_averaged_evaluation.ci_averaged_evaluation
        self.assertTrue(np.isclose(0.833333, see.ap))

    def test_det_eval_voc_01(self) -> None:
        mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=self._mir_root, mir_branch='a', mir_task_id='a', ms=mirpb.MirStorage.MIR_ANNOTATIONS)
        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0.0005
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.need_pr_curve = False
        evaluate_config.class_ids[:] = [3]
        evaluation: mirpb.Evaluation = det_eval_voc.evaluate(prediction=mir_annotations.prediction,
                                                             ground_truth=mir_annotations.ground_truth,
                                                             config=evaluate_config)
        self.assertEqual(evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation.ap, 0)
        self.assertEqual(evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation.ar, 0)

    def test_det_eval_ctl_ops(self) -> None:
        gt_pred_rev_tid = revs_parser.parse_single_arg_rev('a@a', need_tid=False)
        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0.0005
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.need_pr_curve = False
        evaluate_config.main_ck = 'color'
        evaluation = eval_ctl_ops.evaluate_datasets(mir_root=self._mir_root,
                                                        gt_rev_tid=gt_pred_rev_tid,
                                                        pred_rev_tid=gt_pred_rev_tid,
                                                        evaluate_config=evaluate_config)
        self.assertIsNotNone(evaluation)
        self.assertEqual({'blue', 'red'}, set(evaluation.sub_cks.keys()))

        evaluate_config.main_ck = 'FakeMainCk'
        evaluation = eval_ctl_ops.evaluate_datasets(mir_root=self._mir_root,
                                                        gt_rev_tid=gt_pred_rev_tid,
                                                        pred_rev_tid=gt_pred_rev_tid,
                                                        evaluate_config=evaluate_config)
        self.assertIsNone(evaluation)
