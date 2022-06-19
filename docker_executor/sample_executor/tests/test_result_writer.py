import json
import os
import shutil
from typing import List, Dict, Tuple
import unittest

import yaml

from ymir_exc import result_writer as rw, settings


class TestResultWriter(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = os.path.join('/tmp', 'test_tmi', *self.id().split(".")[-3:])
        self._custom_env_file = os.path.join(self._test_root, 'env.yml')
        self._training_result_file = os.path.join(self._test_root, 'out', 'training-result.yaml')
        self._mining_result_file = os.path.join(self._test_root, 'out', 'mining-result.tsv')
        self._infer_result_file = os.path.join(self._test_root, 'out', 'infer-result.json')
        self._monitor_file = os.path.join(self._test_root, 'out', 'monitor.txt')

    def setUp(self) -> None:
        settings.DEFAULT_ENV_FILE_PATH = self._custom_env_file
        self._prepare_dirs()
        self._prepare_env_config()
        return super().setUp()

    def tearDown(self) -> None:
        # self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._test_root)
        os.makedirs(os.path.join(self._test_root, 'out'), exist_ok=True)

    def _prepare_env_config(self) -> None:
        env_obj = {
            'task_id': 'task0',
            'output': {
                'root_dir': os.path.join(self._test_root, 'out'),
                'models_dir': os.path.join(self._test_root, 'out', 'models'),
                'training_result_file': self._training_result_file,
                'mining_result_file': self._mining_result_file,
                'infer_result_file': self._infer_result_file,
                'monitor_file': self._monitor_file,
            },
        }
        with open(self._custom_env_file, 'w') as f:
            yaml.safe_dump(env_obj, f)

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # protected: check results
    def _check_model_stages(self, best_stage_name: str, mAP: float, stage_names: List[str]) -> None:
        with open(self._training_result_file, 'r') as f:
            result_obj: dict = yaml.safe_load(f)
        self.assertEqual(set(stage_names), set(result_obj['model_stages'].keys()))
        self.assertEqual(best_stage_name, result_obj['best_stage_name'])
        self.assertEqual(mAP, result_obj['map'])


    def _check_mining_result(self, mining_result: List[Tuple[str, float]]) -> None:
        with open(self._mining_result_file, 'r') as f:
            lines = f.read().splitlines()
            self.assertEqual(len(lines), len(mining_result))
            self.assertEqual(lines[0], 'b\t0.3')
            self.assertEqual(lines[1], 'c\t0.2')
            self.assertEqual(lines[2], 'a\t0.1')

    def _check_infer_result(self, infer_result: Dict[str, List[rw.Annotation]]) -> None:
        with open(self._infer_result_file, 'r') as f:
            infer_result_obj = json.loads(f.read())
            self.assertEqual(set(infer_result_obj['detection'].keys()), set(infer_result.keys()))

    # public: test cases
    def test_write_model_stage_00(self) -> None:
        stage_names = [f"epoch_{idx}" for idx in range(0, 11)]
        for idx, stage_name in enumerate(stage_names):
            rw.write_model_stage(stage_name=stage_name,
                                 files=[f"model-{idx}.params", 'model-symbol.json'],
                                 mAP=idx / 10,
                                 timestamp=10 * idx + 1000000,
                                 as_best=(idx == 8))
        expected_stage_names = [f"epoch_{idx}" for idx in range(1, 11)]
        self._check_model_stages(stage_names=expected_stage_names, best_stage_name='epoch_8', mAP=0.8)

    def test_write_model_stage_01(self) -> None:
        stage_names = [f"epoch_{idx}" for idx in range(0, 11)]
        for idx, stage_name in enumerate(stage_names):
            rw.write_model_stage(stage_name=stage_name,
                                 files=[f"model-{idx}.params", 'model-symbol.json'],
                                 mAP=idx / 10,
                                 timestamp=10 * idx + 1000000)
        expected_stage_names = [f"epoch_{idx}" for idx in range(1, 11)]
        self._check_model_stages(stage_names=expected_stage_names, best_stage_name='epoch_10', mAP=1.0)

    def test_write_training_result(self) -> None:
        rw.write_training_result(model_names=['fake.model'], mAP=0.9, classAPs={})
        self._check_model_stages(stage_names=['default_stage'], best_stage_name='default_stage', mAP=0.9)

    def test_write_mining_result(self) -> None:
        mining_result = [('a', '0.1'), ('b', '0.3'), ('c', '0.2')]
        rw.write_mining_result(mining_result=mining_result)
        self._check_mining_result(mining_result=mining_result)

    def test_write_infer_result(self) -> None:
        infer_result = {
            'a': [
                rw.Annotation(box=rw.Box(x=0, y=0, w=50, h=50), class_name='cat', score=0.2),
                rw.Annotation(box=rw.Box(x=150, y=0, w=50, h=50), class_name='person', score=0.3)
            ],
            'b': [rw.Annotation(box=rw.Box(x=0, y=0, w=50, h=150), class_name='person', score=0.2)],
            'c': [],
        }
        rw.write_infer_result(infer_result=infer_result)
        self._check_infer_result(infer_result=infer_result)
