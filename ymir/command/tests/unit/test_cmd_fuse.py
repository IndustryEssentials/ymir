import os
import shutil
import unittest

from mir.commands.fuse import CmdFuse
from mir.tools.code import MirCode
import tests.utils as test_utils


class TestCmdFuse(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        test_utils.remake_dirs(self._mir_root)
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        # if os.path.isdir(self._mir_root):
        #     shutil.rmtree(self._mir_root)
        return super().tearDown()

    # protected: prepare env
    def _prepare_mir_repo(self) -> None:
        test_utils.mir_repo_init(self._mir_root)
        test_utils.prepare_labels(mir_root=self._mir_root, names=['fish', 'person', 'cat'])
        self._prepare_mir_branch_a()
        self._prepare_mir_branch_b()

    def _prepare_mir_branch_a(self):
        """
        assets and keywords:
            a: a0(1), a1(1), a2(1), a3(1)
        all asset size set to (1000, 1000)
        """
        assets_and_keywords = {
            "a0": ([1], {
                "c0": "c1"
            }),
            "a1": ([1], {
                "c0": "c1"
            }),
            "a2": ([1], {
                "c0": "c1"
            }),
            "a3": ([1], {
                "c0": "c1"
            }),
        }
        test_utils.prepare_mir_branch(mir_root=self._mir_root,
                                      assets_and_keywords=assets_and_keywords,
                                      size=1000,
                                      branch_name_and_task_id="a",
                                      commit_msg="prepare_branch_merge_a")

    def _prepare_mir_branch_b(self):
        """
        assets and keywords:
            b: b0(2), b1(2), b2(2)
        all asset size set to (1100, 1100)
        """
        assets_and_keywords = {
            "b0": ([2], {
                "c0": "c2"
            }),
            "b1": ([2], {
                "c0": "c2"
            }),
            "b2": ([2], {
                "c0": "c2"
            }),
        }
        test_utils.prepare_mir_branch(mir_root=self._mir_root,
                                      assets_and_keywords=assets_and_keywords,
                                      size=1100,
                                      branch_name_and_task_id="b",
                                      commit_msg="prepare_branch_merge_b")

    # public: test cases
    def test_fuse_00(self) -> None:
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.label_storage_file = os.path.join(self._mir_root, '.mir', 'labels.yaml')
        fake_args.dst_rev = 'c@test_fuse_00'
        fake_args.work_dir = ''
        fake_args.src_revs = 'b;a'
        fake_args.ex_src_revs = ''
        fake_args.strategy = 'stop'
        fake_args.in_cis = 'person;cat'
        fake_args.ex_cis = ''
        fake_args.filter_anno_src = 'any'
        fake_args.count = 0
        fake_args.rate = 0.5
        fuse_instance = CmdFuse(fake_args)
        ret = fuse_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)