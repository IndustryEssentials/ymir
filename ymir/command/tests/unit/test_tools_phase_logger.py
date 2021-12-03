import math
import os
import shutil
import unittest
from unittest import mock

from mir.tools.phase_logger import PhaseLogger, PhaseLoggerCenter, PhaseStateEnum

from tests import utils as test_utils


class TestPhaseLogger(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._monitor_file = os.path.join(self._test_root, 'monitor.txt')

    # protected: prepare and deprepare
    @staticmethod
    def _prepare_dir(test_root: str):
        if os.path.isdir(test_root):
            shutil.rmtree(test_root)
        os.makedirs(test_root, exist_ok=True)

    @staticmethod
    def _deprepare_dir(test_root: str):
        if os.path.isdir(test_root):
            shutil.rmtree(test_root)

    # protected: check result
    def _check_monitor_file(self, task_name: str, global_percent: float, task_state: str, trace_message: str):
        trace_message_line_count = len(trace_message.splitlines()) if trace_message else 0
        with open(self._monitor_file, 'r') as f:
            monitor_lines = f.read().splitlines()
            self.assertEqual(1 + trace_message_line_count, len(monitor_lines))
            monitor_parts = monitor_lines[0].split('\t')
            self.assertEqual(4, len(monitor_parts))
            self.assertEqual(task_name, monitor_parts[0])
            self.assertEqual(f"{global_percent:.2f}", monitor_parts[2])
            self.assertEqual(task_state, monitor_parts[3])

            if trace_message:
                self.assertEqual(trace_message.splitlines(), monitor_lines[1:])

    # public: test cases
    def test_constructor(self):
        # normal cases
        pm = PhaseLogger(task_name='task_name')
        self.assertEqual('task_name', pm.task_name)
        self.assertEqual(None, pm.monitor_file)
        self.assertEqual(0.0, pm.start_percent)
        self.assertEqual(1.0, pm.end_percent)
        self.assertEqual(0.0, pm.global_percent)

        pm = PhaseLogger(task_name='task_name', monitor_file='/tmp/monitor.txt')
        self.assertEqual('task_name', pm.task_name)
        self.assertEqual('/tmp/monitor.txt', pm.monitor_file)
        self.assertEqual(0.0, pm.start_percent)
        self.assertEqual(1.0, pm.end_percent)
        self.assertEqual(0.0, pm.global_percent)

        pm = PhaseLogger(task_name='task_name', monitor_file='/tmp/monitor.txt', start=0.5, end=0.7)
        self.assertEqual('task_name', pm.task_name)
        self.assertEqual('/tmp/monitor.txt', pm.monitor_file)
        self.assertEqual(0.5, pm.start_percent)
        self.assertEqual(0.7, pm.end_percent)
        self.assertEqual(0.5, pm.global_percent)

        # abnormal cases
        with self.assertRaises(Exception):
            PhaseLogger(task_name=None)
        with self.assertRaises(Exception):
            PhaseLogger(task_name='task_name', start=-1.0)
        with self.assertRaises(Exception):
            PhaseLogger(task_name='task_name', end=2.0)
        with self.assertRaises(Exception):
            PhaseLogger(task_name='task_name', start=0.5, end=0.3)

    def test_create_children(self):
        # normal cases
        pm = PhaseLogger(task_name='task_name', monitor_file='/tmp/monitor.txt')
        pm_children = pm.create_children(deltas=[0.1, 0.2, 0.3, 0.4])
        self.assertEqual(4, len(pm_children))
        expected_starts = [0.0, 0.1, 0.3, 0.6]
        expected_ends = [0.1, 0.3, 0.6, 1.0]
        for idx, child in enumerate(pm_children):
            self.assertTrue(math.isclose(expected_starts[idx], child.start_percent))
            self.assertTrue(math.isclose(expected_ends[idx], child.end_percent))
            self.assertTrue(math.isclose(expected_starts[idx], child.global_percent))
            self.assertEqual(0.0, child.local_percent)
            self.assertEqual('task_name', child.task_name)
            self.assertEqual('/tmp/monitor.txt', child.monitor_file)

        pm = PhaseLogger(task_name='task_name', monitor_file='/tmp/monitor.txt', start=0.2, end=0.8)
        pm_children = pm.create_children(deltas=[0.1, 0.2, 0.3, 0.4])
        expected_starts = [0.2, 0.26, 0.38, 0.56]
        expected_ends = [0.26, 0.38, 0.56, 0.8]
        for idx, child in enumerate(pm_children):
            self.assertTrue(math.isclose(expected_starts[idx], child.start_percent))
            self.assertTrue(math.isclose(expected_ends[idx], child.end_percent))
            self.assertTrue(math.isclose(expected_starts[idx], child.global_percent))
            self.assertEqual(0.0, child.local_percent)
            self.assertEqual('task_name', child.task_name)
            self.assertEqual('/tmp/monitor.txt', child.monitor_file)

        # abnormal cases
        with self.assertRaises(Exception):
            pm.create_children(deltas=[])
        with self.assertRaises(Exception):
            pm.create_children(deltas=[1, 2, 3, 4, 5])
        with self.assertRaises(Exception):
            pm.create_children(deltas=[0.0, 1.0])
        with self.assertRaises(Exception):
            pm.create_children(deltas=[0.5, -0.4, 0.5, 0.4])

    def test_single_write(self):
        # no monitor_file assigned
        pm = PhaseLogger(task_name='task_name')
        pm.update_percent_info(0.5, PhaseStateEnum.RUNNING, None)  # expect to do nothing

        # monitor_file assigned
        TestPhaseLogger._prepare_dir(self._test_root)

        pm = PhaseLogger(task_name='task_name', monitor_file=self._monitor_file)
        pm.update_percent_info(local_percent=0.1, task_state=PhaseStateEnum.RUNNING)
        self._check_monitor_file(task_name=pm.task_name, global_percent=0.1, task_state='running', trace_message=None)
        pm.update_percent_info(local_percent=0.5, task_state=PhaseStateEnum.RUNNING)
        self._check_monitor_file(task_name=pm.task_name, global_percent=0.5, task_state='running', trace_message=None)
        pm.update_percent_info(local_percent=1, task_state=PhaseStateEnum.DONE)
        self._check_monitor_file(task_name=pm.task_name, global_percent=1, task_state='done', trace_message=None)

        TestPhaseLogger._deprepare_dir(self._test_root)

    def test_children_write(self):
        TestPhaseLogger._prepare_dir(self._test_root)

        pm = PhaseLogger(task_name='task_name', monitor_file=self._monitor_file)
        pm_children = pm.create_children(deltas=[0.4, 0.6])

        # child 0 write
        pm_children[0].update_percent_info(local_percent=0.1, task_state=PhaseStateEnum.RUNNING)
        self._check_monitor_file(task_name=pm.task_name, global_percent=0.04, task_state='running', trace_message=None)
        pm_children[0].update_percent_info(local_percent=0.9, task_state=PhaseStateEnum.RUNNING)
        self._check_monitor_file(task_name=pm.task_name, global_percent=0.36, task_state='running', trace_message=None)

        # child 1 write
        pm_children[1].update_percent_info(local_percent=0.1, task_state=PhaseStateEnum.RUNNING)
        self._check_monitor_file(task_name=pm.task_name, global_percent=0.46, task_state='running', trace_message=None)
        pm_children[1].update_percent_info(local_percent=1.0, task_state=PhaseStateEnum.DONE, trace_message='task done')
        self._check_monitor_file(task_name=pm.task_name, global_percent=1, task_state='done', trace_message='task done')

        TestPhaseLogger._deprepare_dir(self._test_root)


class TestPhaseLoggerCenter(unittest.TestCase):
    # protected: mock functions
    def _mock_update(*args, **kwargs):
        pass

    @mock.patch('mir.tools.phase_logger.PhaseLogger.update_percent_info', side_effect=_mock_update)
    def test_00(self, mock_run):
        PhaseLoggerCenter.create_phase_loggers('copy', None, '0')
        sub_phase_loggers = PhaseLoggerCenter.loggers()

        sub_logger: PhaseLogger = sub_phase_loggers['copy.read']
        self.assertTrue(math.isclose(0, sub_logger.start_percent))
        self.assertTrue(math.isclose(0.4, sub_logger.end_percent))
        self.assertFalse(sub_logger.auto_done)

        sub_logger: PhaseLogger = sub_phase_loggers['copy.new']
        self.assertTrue(math.isclose(0.6, sub_logger.start_percent))
        self.assertTrue(math.isclose(1.0, sub_logger.end_percent))
        self.assertTrue(sub_logger.auto_done)

        PhaseLoggerCenter.update_phase('copy.read', task_state=PhaseStateEnum.DONE, trace_message='abc')
        mock_run.assert_called_with(local_percent=1, task_state=PhaseStateEnum.DONE,
                                    state_code=0, state_content=None, trace_message='abc')

        PhaseLoggerCenter.clear_all()

    def test_01(self):
        PhaseLoggerCenter.create_phase_loggers('export', None, '0')
        PhaseLoggerCenter.update_phase('export.others', task_state=PhaseStateEnum.DONE, trace_message='export done')
        self.assertEqual(1.0, PhaseLoggerCenter.loggers()['export.others'].global_percent)

        PhaseLoggerCenter.clear_all()
