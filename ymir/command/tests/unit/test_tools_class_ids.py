import os
import shutil
import unittest

from mir.tools.class_ids import ClassIdManager
from tests import utils as test_utils


class TestToolsClassIds(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self._prepare_dirs()
        self._prepare_label_file()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self) -> None:
        test_utils.remake_dirs(self._test_root)

    def _deprepare_dirs(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def _prepare_label_file(self) -> None:
        test_utils.prepare_labels(mir_root=self._test_root, names=['a', 'b', 'c'])

    # public: test cases
    def test_read(self) -> None:
        cim = ClassIdManager(self._test_root)
        self.assertEqual([0, 1, 2], cim.all_ids())
        self.assertEqual([0, 1, 2], cim.id_for_names(['a', 'b', 'c'])[0])

    def test_write(self) -> None:
        cim = ClassIdManager(self._test_root)
        self.assertEqual((3, 'd'), cim.add_main_name('D'))
        self.assertEqual((4, 'e'), cim.add_main_name(' e '))
        self.assertEqual([0, 1, 2, 3, 4], cim.all_ids())
        self.assertEqual([0, 1, 2, 3, 4], cim.id_for_names(['a', 'b', 'c', 'd', 'e'])[0])

    def test_write_abnormal(self) -> None:
        cim = ClassIdManager(self._test_root)
        cim.add_main_name('a')
        self.assertEqual([0, 1, 2], cim.all_ids())
        self.assertEqual([0, 1, 2], cim.id_for_names(['a', 'b', 'c'])[0])
