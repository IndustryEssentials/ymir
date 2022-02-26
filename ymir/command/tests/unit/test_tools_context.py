import os
import shutil
import unittest

from mir.tools import context
from tests import utils as test_utils


class TestToolsContext(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self._prepare_dirs()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        test_utils.remake_dirs(os.path.join(self._test_root, '.mir'))

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # test cases
    def test_00(self):
        context_config = context.ContextConfig()

        # case 1
        context_config.project.class_ids = [1, 2, 3]
        context.save(mir_root=self._test_root, context_config=context_config)

        saved_context_config = context.load(mir_root=self._test_root)
        self.assertEqual(context_config, saved_context_config)

        # case 2
        context_config = context.ContextConfig()
        context.save(mir_root=self._test_root, context_config=context_config)

        saved_context_config = context.load(mir_root=self._test_root)
        self.assertEqual(context_config, saved_context_config)
