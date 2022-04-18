import os
import shutil
import unittest

import yaml

from executor import env, monitor


class TestMonitor(unittest.TestCase):
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

        env.set_env(self._custom_env_file)

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # protected: check results
    def _check_monitor(self, percent: float, error_occured: bool) -> None:
        with open(self._monitor_file, 'r') as f:
            lines = f.read().splitlines()
        task_id, timestamp_str, percent_str, state_str, *_ = lines[0].split()
        self.assertEqual(task_id, env.get_current_env().task_id)
        self.assertTrue(float(timestamp_str) > 0)
        self.assertEqual(percent, float(percent_str))
        if error_occured:
            self.assertEqual(4, int(state_str))
            self.assertTrue(len(lines) > 1)
        else:
            self.assertEqual(2, int(state_str))
            self.assertEqual(len(lines), 1)

    # public: test cases
    def test_write_monitor(self) -> None:
        monitor.write_monitor_logger(info='a fake log info', percent=0.2)
        self._check_monitor(percent=0.2, error_occured=False)

        monitor.write_monitor_logger(info='another fake log info', percent=0.4, error_occured=True)
        self._check_monitor(percent=1.0, error_occured=True)
