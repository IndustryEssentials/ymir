import os
import shutil
import unittest

import yaml

from tests import utils as test_utils


class TestCmdSandboxVersion(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._sandbox_a_root = os.path.join(self._test_root, 'sandbox_a')
        self._sandbox_b_root = os.path.join(self._test_root, 'sandbox_b')
        self._sandbox_c_root = os.path.join(self._test_root, 'sandbox_c')

    def setUp(self) -> None:
        self._prepare_test_root()
        self._prepare_sandbox_a()
        self._prepare_sandbox_b()
        self._prepare_sandbox_c()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_test_root()
        return super().tearDown()

    # prepare and de-prepare
    def _prepare_test_root(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._test_root, exist_ok=True)

    def _deprepare_test_root(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def _prepare_sandbox_a(self) -> None:
        """
        sandbox a: sandbox with two users
        """
        os.makedirs(self._sandbox_a_root)

        for user_id, repo_ids in {'0001': ['000001', '000002'], '0002': ['000001']}.items():
            os.makedirs(os.path.join(self._sandbox_a_root, user_id))

            for repo_id in repo_ids:
                os.makedirs(os.path.join(self._sandbox_a_root, user_id, repo_id))

            labels_dict = {'labels': [], 'version': 1, 'ymir_version': '0.4.2'}
            with open(os.path.join(self._sandbox_a_root, user_id, 'labels.yaml'), 'w') as f:
                yaml.safe_dump(labels_dict, f)

    def _prepare_sandbox_b(self) -> None:
        """
        sandbox b: an empty sandbox
        """
        os.makedirs(self._sandbox_b_root)

    def _prepare_sandbox_c(self) -> None:
        """
        sandbox c: sandbox with multiple user space versions
        """
        pass
