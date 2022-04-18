import json
import os
import shutil
from typing import List, Dict, Tuple
import unittest

import yaml

from executor import result_writer as rw, settings


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
    def _check_training_result(self, model_names: List[str], mAP: float, classAPs: Dict[str, float], **kwargs) -> None:
        with open(self._training_result_file, 'r') as f:
            result_obj = yaml.safe_load(f)
            self.assertEqual(result_obj['model'], model_names)
            self.assertEqual(result_obj['map'], mAP)
            self.assertEqual(result_obj['class_aps'], classAPs)
            for k, v in kwargs.items():
                self.assertEqual(result_obj[k], v)

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

    def test_write_training_result(self) -> None:
        model_names = ['model-symbols.json', 'model-0000.params']
        mAP = 0.86
        classAPs = {'cat': 0.86, 'person': 0.86}
        rw.write_training_result(model_names=model_names, mAP=mAP, classAPs=classAPs, author='fake author')
        self._check_training_result(model_names=model_names, mAP=mAP, classAPs=classAPs, author='fake author')

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
