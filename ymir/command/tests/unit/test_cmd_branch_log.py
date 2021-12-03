import os
import shutil
import unittest

from mir.commands.branch import CmdBranch
from mir.commands.log import CmdLog
from mir.tools.code import MirCode

from tests import utils as test_utils


class TestCmdBranchAndLog(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self.__prepare_dir(self._mir_root)
        self.__prepare_mir_repo(self._mir_root)
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dir(self._mir_root)
        return super().tearDown()

    # private: prepare
    def __prepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)
        os.makedirs(mir_root, exist_ok=True)

    def __deprepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)

    def __prepare_mir_repo(self, mir_root: str):
        test_utils.mir_repo_init(self._mir_root)

    # public: test cases
    def test_00(self):
        # test branch
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.force_delete = None
        cmd_instance = CmdBranch(fake_args)
        self.assertEqual(MirCode.RC_OK, cmd_instance.run())

        fake_args.force_delete = 'master'
        cmd_instance = CmdBranch(fake_args)
        self.assertNotEqual(MirCode.RC_OK, cmd_instance.run())

        # test log
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.decorate = False
        fake_args.oneline = False
        fake_args.graph = False
        fake_args.dog = False
        cmd_instance = CmdLog(fake_args)
        self.assertEqual(MirCode.RC_OK, cmd_instance.run())
