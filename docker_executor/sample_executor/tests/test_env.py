import os
import shutil
import unittest

import yaml

from executor.env import get_current_env, get_executor_config, set_env


class TestEnv(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = os.path.join('/tmp', 'test_tmi', *self.id().split(".")[-3:])
        self._custom_env_file = os.path.join(self._test_root, 'env.yml')
        self._training_index_file = os.path.join(self._test_root, 'training-index.tsv')
        self._executor_config_file = os.path.join(self._test_root, 'config.yaml')
        self._expected_executor_config = {
            'gpu_id': '0',
            'image_size': 480,
        }

    def setUp(self) -> None:
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
                'config_file': self._executor_config_file,
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

        # executor config
        with open(self._executor_config_file, 'w') as f:
            yaml.safe_dump(self._expected_executor_config, f)

        # training index
        with open(self._training_index_file, 'w') as f:
            f.write('/in/assets/0.jpg\t/in/assets/0.txt\n')
            f.write('/in/assets/1.jpg\t/in/assets/1.txt\n')
            f.write('/in/assets/2.jpg\t/in/assets/2.txt\n')

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def test_00(self) -> None:
        set_env(env_file_path=self._custom_env_file)

        self.assertEqual(get_current_env().task_id, 'task0')
        self.assertTrue(get_current_env().run_training)
        self.assertFalse(get_current_env().run_mining)
        self.assertFalse(get_current_env().run_infer)
        self.assertEqual(get_current_env().input.root_dir, '/in1')
        self.assertEqual(get_current_env().input.val_index_file, '')

        executor_config = get_executor_config()
        self.assertEqual(executor_config, self._expected_executor_config)
