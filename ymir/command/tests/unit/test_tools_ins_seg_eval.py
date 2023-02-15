import json
import os
import shutil
from typing import Tuple
import unittest

from google.protobuf import json_format
import numpy as np

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import det_eval_ops
from tests import utils as test_utils


class TestToolsSegEval(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._work_dir = os.path.join(self._test_root, 'work_dir')
        self._mir_root = os.path.join(self._test_root, 'mir_root')

    def setUp(self) -> None:
        self._prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['tv', 'car', 'person', 'dog', 'cat'])
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
            filepath=os.path.join('tests', 'assets', 'test_seg_eval.json'))

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0
        evaluate_config.iou_thrs_interval = '0.5'
        evaluate_config.class_ids[:] = [2, 4]
        evaluate_config.type = mirpb.ObjectType.OT_SEG
        evaluate_config.is_instance_segmentation = True

        evaluation = det_eval_ops.det_evaluate_with_pb(prediction=mir_annotations.prediction,
                                                       ground_truth=mir_annotations.ground_truth,
                                                       config=evaluate_config,
                                                       assets_metadata=mir_metadatas)

        # check result
        iou_ci_averaged = evaluation.dataset_evaluation.iou_averaged_evaluation.ci_averaged_evaluation
        self.assertTrue(np.isclose(0.35973597, iou_ci_averaged.ap, atol=1e-8))
        self.assertTrue(np.isclose(0.5, iou_ci_averaged.ar))

    def test_sem_seg_eval_00(self) -> None:
        mir_metadatas, mir_annotations = self._load_mirdatas(
            filepath=os.path.join('tests', 'assets', 'test_seg_eval.json'))

        evaluate_config = mirpb.EvaluateConfig()
        evaluate_config.conf_thr = 0
        evaluate_config.iou_thrs_interval = '0'
        evaluate_config.class_ids[:] = [2, 4]
        evaluate_config.type = mirpb.ObjectType.OT_SEG
        evaluate_config.is_instance_segmentation = False

        evaluation = det_eval_ops.det_evaluate_with_pb(prediction=mir_annotations.prediction,
                                                       ground_truth=mir_annotations.ground_truth,
                                                       config=evaluate_config,
                                                       assets_metadata=mir_metadatas)

        # check result
        semseg_metrics = evaluation.dataset_evaluation.segmentation_metrics
        self.assertTrue(np.isclose(0.83443254, semseg_metrics.aAcc, atol=1e-8))
        self.assertTrue(np.isclose(0.79606306, semseg_metrics.mAcc, atol=1e-8))
        self.assertTrue(np.isclose(0.79110819, semseg_metrics.mIoU, atol=1e-8))
