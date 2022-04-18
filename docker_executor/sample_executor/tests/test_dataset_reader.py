import os
import shutil
import unittest

import yaml

from executor import dataset_reader as dr, env, settings


class TestDatasetReader(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = os.path.join('/tmp', 'test_tmi', *self.id().split(".")[-3:])
        self._custom_env_file = os.path.join(self._test_root, 'env.yml')
        self._training_index_file = os.path.join(self._test_root, 'training-index.tsv')

    def setUp(self) -> None:
        settings.DEFAULT_ENV_FILE_PATH = self._custom_env_file
        self._prepare_dirs()
        self._prepare_assets()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._test_root, exist_ok=True)

    def _prepare_assets(self) -> None:
        # env
        env_obj = {
            'task_id': 'task0',
            'run_training': True,
            'run_mining': False,
            'run_infer': False,
            'input': {
                'root_dir': '/in1',
                'assets_dir': '/in1/assets',
                'annotations_dir': '/in1/annotations',
                'models_dir': '/in1/models',
                'training_index_file': self._training_index_file,
            },
            'output': {
                'root_dir': '/out1',
                'models_dir': '/out1/models',
                'tensorboard_dir': '/out1/tensorboard',
                'training_result_file': '/out1/models/result.tsv',
                'mining_result_file': '/out1/result.txt',
                'infer_result_file': '/out1/infer-result.json',
                'monitor_file': '/out1/monitor.txt',
            },
        }
        with open(self._custom_env_file, 'w') as f:
            yaml.safe_dump(env_obj, f)

        # training index
        with open(self._training_index_file, 'w') as f:
            f.write('/in/assets/0.jpg\t/in/assets/0.txt\n')
            f.write('/in/assets/1.jpg\t/in/assets/1.txt\n')
            f.write('/in/assets/2.jpg\t/in/assets/2.txt\n')

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def test_00(self) -> None:
        training_list = list(dr.item_paths(dataset_type=dr.DatasetType.TRAINING))
        self.assertEqual(len(training_list), 3)  # have 3 items
        self.assertEqual(len(training_list[0]), 2)  # each item have asset and annotations

        try:
            dr.item_paths(dataset_type=dr.DatasetType.VALIDATION)
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
        try:
            dr.item_paths(dataset_type=dr.DatasetType.CANDIDATE)
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
