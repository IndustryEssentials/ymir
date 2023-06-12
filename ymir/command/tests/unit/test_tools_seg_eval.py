import json
import os
import shutil
from typing import Tuple
import unittest

from google.protobuf import json_format
import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools.eval import eval_ops
from tests import utils as test_utils


class TestToolsSegEval(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._work_dir = os.path.join(self._test_root, 'work_dir')
        self._mir_root = os.path.join(self._test_root, 'mir_root')

    def setUp(self) -> None:
        self._prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['tv', 'background', 'person', 'foreground', 'cat'])
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        test_utils.remake_dirs(self._work_dir)
        test_utils.remake_dirs(self._mir_root)

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # protected: misc
    @classmethod
    def _load_mirdatas(cls, filepath: str) -> Tuple[mirpb.MirMetadatas, mirpb.MirAnnotations]:
        with open(filepath, 'r') as f:
            d = json.loads(f.read())
            test_utils.convert_dict_str_keys_to_int(d)
        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(js_dict=d['mir_metadatas'], message=mir_metadatas)
        json_format.ParseDict(js_dict=d['mir_annotations'], message=mir_annotations)
        return mir_metadatas, mir_annotations

    # public: test cases
    def test_ins_seg_eval_00(self) -> None:
        mir_metadatas, mir_annotations = self._load_mirdatas(
            filepath=os.path.join('tests', 'assets', 'test_eval_ins_seg.json'))

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.class_ids[:] = [2, 4]
        evaluate_config.type = mirpb.ObjectType.OT_INS_SEG

        evaluation = eval_ops.evaluate_with_pb(prediction=mir_annotations.prediction,
                                               ground_truth=mir_annotations.ground_truth,
                                               config=evaluate_config,
                                               assets_metadata=mir_metadatas)

        # check result
        iou_ci_averaged = evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
        self.assertTrue(np.isclose(0.35973597, iou_ci_averaged.maskAP, atol=1e-8))
        self.assertTrue(np.isclose(0.37376236, iou_ci_averaged.boxAP, atol=1e-8))
        self.assertTrue(np.isclose(0.5, iou_ci_averaged.ar, atol=1e-8))
        self.assertEqual(0, iou_ci_averaged.ap)

        # check result: confusion matrix and linked id
        #   key: (asset_id, annotation_index), value: (cm, det_link_id)
        expected_aid_idx_to_cm_lids_pred = {
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 0): (mirpb.ConfusionMatrixType.FP, -1),
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 2): (mirpb.ConfusionMatrixType.TP, 0),
            ('2be80df459618f1ef797025f070d94eae91aeea1', 0): (mirpb.ConfusionMatrixType.FP, -1),
            ('2be80df459618f1ef797025f070d94eae91aeea1', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('2edb4989439783e39a304ef0fd0f3531407e13f7', 0): (mirpb.ConfusionMatrixType.FP, -1),
            ('2edb4989439783e39a304ef0fd0f3531407e13f7', 1): (mirpb.ConfusionMatrixType.TP, 0),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 0): (mirpb.ConfusionMatrixType.TP, 1),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 2): (mirpb.ConfusionMatrixType.FP, -1),
            ('c4f07b4e1882467d51613b35fce361d7c8644d99', 0): (mirpb.ConfusionMatrixType.FP, -1),
            ('c4f07b4e1882467d51613b35fce361d7c8644d99', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('c4f07b4e1882467d51613b35fce361d7c8644d99', 2): (mirpb.ConfusionMatrixType.FP, -1)
        }
        expected_aid_idx_to_cm_lids_gt = {
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 0): (mirpb.ConfusionMatrixType.MTP, 2),
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 1): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('1cffe0b236ca20bcc94c82379eea2c8e76df6f66', 2): (mirpb.ConfusionMatrixType.FN, -1),
            ('2be80df459618f1ef797025f070d94eae91aeea1', 0): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('2edb4989439783e39a304ef0fd0f3531407e13f7', 0): (mirpb.ConfusionMatrixType.MTP, 1),
            ('2edb4989439783e39a304ef0fd0f3531407e13f7', 1): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('2edb4989439783e39a304ef0fd0f3531407e13f7', 2): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 0): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 1): (mirpb.ConfusionMatrixType.MTP, 0),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 2): (mirpb.ConfusionMatrixType.FN, -1),
            ('825b94f9ab9e09660ef31644f4facd740dd91db3', 3): (mirpb.ConfusionMatrixType.IGNORED, -1),
            ('c4f07b4e1882467d51613b35fce361d7c8644d99', 0): (mirpb.ConfusionMatrixType.FN, -1),
            ('c4f07b4e1882467d51613b35fce361d7c8644d99', 1): (mirpb.ConfusionMatrixType.IGNORED, -1)
        }
        for asset_id, sia in mir_annotations.prediction.image_annotations.items():
            for oa in sia.boxes:
                self.assertEqual(expected_aid_idx_to_cm_lids_pred[(asset_id, oa.index)], (oa.cm, oa.det_link_id))
        for asset_id, sia in mir_annotations.ground_truth.image_annotations.items():
            for oa in sia.boxes:
                self.assertEqual(expected_aid_idx_to_cm_lids_gt[(asset_id, oa.index)], (oa.cm, oa.det_link_id))

    def test_sem_seg_eval_00(self) -> None:
        mir_metadatas, mir_annotations = self._load_mirdatas(
            filepath=os.path.join('tests', 'assets', 'test_eval_sem_seg.json'))

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.class_ids[:] = [1, 3]
        evaluate_config.type = mirpb.ObjectType.OT_SEM_SEG

        evaluation = eval_ops.evaluate_with_pb(prediction=mir_annotations.prediction,
                                               ground_truth=mir_annotations.ground_truth,
                                               config=evaluate_config,
                                               assets_metadata=mir_metadatas)

        # check result
        semseg_metrics = evaluation.dataset_evaluation.segmentation_metrics
        self.assertTrue(np.isclose(0.69962458, semseg_metrics.aAcc, atol=1e-7))
        self.assertTrue(np.isclose(0.65295724, semseg_metrics.mAcc, atol=1e-7))
        self.assertTrue(np.isclose(0.50211951, semseg_metrics.mIoU, atol=1e-7))

        expected_aid_idx_to_cm_lids_pred = {
            ('33a12aff2fbf56c013d739c5ab2b95125f7bd76f', 0): (mirpb.ConfusionMatrixType.TP, -1),
            ('33a12aff2fbf56c013d739c5ab2b95125f7bd76f', 1): (mirpb.ConfusionMatrixType.TP, -1),
            ('4dc96d7dbe2338ad884a490161fe7a83b777a23e', 0): (mirpb.ConfusionMatrixType.TP, -1),
            ('4dc96d7dbe2338ad884a490161fe7a83b777a23e', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('5f65e89f247dff226d287ca11ea67ea4f5d73036', 0): (mirpb.ConfusionMatrixType.TP, -1),
            ('5f65e89f247dff226d287ca11ea67ea4f5d73036', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('85e66576063a9a8807ac2ab0b5f9ada1d4e862dc', 0): (mirpb.ConfusionMatrixType.TP, -1),
            ('85e66576063a9a8807ac2ab0b5f9ada1d4e862dc', 1): (mirpb.ConfusionMatrixType.FP, -1),
            ('cd994692a4907f4684b5d845e18010b39d412fc2', 0): (mirpb.ConfusionMatrixType.FP, -1),
            ('cd994692a4907f4684b5d845e18010b39d412fc2', 1): (mirpb.ConfusionMatrixType.FP, -1)
        }
        expected_aid_idx_to_cm_lids_gt = {
            ('33a12aff2fbf56c013d739c5ab2b95125f7bd76f', 0): (mirpb.ConfusionMatrixType.MTP, -1),
            ('33a12aff2fbf56c013d739c5ab2b95125f7bd76f', 1): (mirpb.ConfusionMatrixType.MTP, -1),
            ('4dc96d7dbe2338ad884a490161fe7a83b777a23e', 0): (mirpb.ConfusionMatrixType.FN, -1),
            ('4dc96d7dbe2338ad884a490161fe7a83b777a23e', 1): (mirpb.ConfusionMatrixType.MTP, -1),
            ('5f65e89f247dff226d287ca11ea67ea4f5d73036', 0): (mirpb.ConfusionMatrixType.FN, -1),
            ('5f65e89f247dff226d287ca11ea67ea4f5d73036', 1): (mirpb.ConfusionMatrixType.MTP, -1),
            ('85e66576063a9a8807ac2ab0b5f9ada1d4e862dc', 0): (mirpb.ConfusionMatrixType.FN, -1),
            ('85e66576063a9a8807ac2ab0b5f9ada1d4e862dc', 1): (mirpb.ConfusionMatrixType.MTP, -1),
            ('cd994692a4907f4684b5d845e18010b39d412fc2', 0): (mirpb.ConfusionMatrixType.FN, -1),
            ('cd994692a4907f4684b5d845e18010b39d412fc2', 1): (mirpb.ConfusionMatrixType.FN, -1)
        }
        # check result: confusion matrix
        for asset_id, sia in mir_annotations.prediction.image_annotations.items():
            for oa in sia.boxes:
                self.assertEqual(expected_aid_idx_to_cm_lids_pred[(asset_id, oa.index)], (oa.cm, oa.det_link_id))
        for asset_id, sia in mir_annotations.ground_truth.image_annotations.items():
            for oa in sia.boxes:
                self.assertEqual(expected_aid_idx_to_cm_lids_gt[(asset_id, oa.index)], (oa.cm, oa.det_link_id))

    def test_sem_seg_eval_01(self) -> None:
        mir_metadatas, mir_annotations = self._load_mirdatas(
            filepath=os.path.join('tests', 'assets', 'test_eval_sem_seg.json'))

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0
        evaluate_config.iou_thrs_interval = ''
        evaluate_config.class_ids[:] = [1, 3]
        evaluate_config.type = mirpb.ObjectType.OT_SEM_SEG

        evaluation = eval_ops.evaluate_with_pb(prediction=mir_annotations.prediction,
                                               ground_truth=mir_annotations.ground_truth,
                                               config=evaluate_config,
                                               assets_metadata=mir_metadatas)

        # check result
        semseg_metrics = evaluation.dataset_evaluation.segmentation_metrics
        self.assertTrue(np.isclose(0.69962458, semseg_metrics.aAcc, atol=1e-7))
        self.assertTrue(np.isclose(0.65295724, semseg_metrics.mAcc, atol=1e-7))
        self.assertTrue(np.isclose(0.50211951, semseg_metrics.mIoU, atol=1e-7))

        # check result: confusion matrix
        for sia in mir_annotations.prediction.image_annotations.values():
            for oa in sia.boxes:
                self.assertEqual(-1, oa.det_link_id)
                self.assertEqual(mirpb.ConfusionMatrixType.NotSet, oa.cm)
        for sia in mir_annotations.ground_truth.image_annotations.values():
            for oa in sia.boxes:
                self.assertEqual(-1, oa.det_link_id)
                self.assertEqual(mirpb.ConfusionMatrixType.NotSet, oa.cm)
