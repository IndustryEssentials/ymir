import multiprocessing as mp
import os
import shutil
import unittest

from mir.tools.class_ids import load_or_create_userlabels, ids_file_path
from tests import utils as test_utils


class TestToolsClassIds(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._label_storage_file = ids_file_path(self._test_root)

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
        cim = load_or_create_userlabels(label_storage_file=self._label_storage_file)
        self.assertEqual([0, 1, 2], cim.all_ids())
        self.assertEqual([0, 1, 2], cim.id_for_names(['a', 'b', 'c'])[0])

    def test_write(self) -> None:
        cim = load_or_create_userlabels(label_storage_file=self._label_storage_file)
        self.assertEqual((3, 'd'), cim.add_main_name('D'))
        self.assertEqual((4, 'e'), cim.add_main_name(' e '))
        self.assertEqual([0, 1, 2, 3, 4], cim.all_ids())
        self.assertEqual([0, 1, 2, 3, 4], cim.id_for_names(['a', 'b', 'c', 'd', 'e'])[0])

    def test_write_abnormal(self) -> None:
        cim = load_or_create_userlabels(label_storage_file=self._label_storage_file)
        cim.add_main_name('a')
        self.assertEqual([0, 1, 2], cim.all_ids())
        self.assertEqual([0, 1, 2], cim.id_for_names(['a', 'b', 'c'])[0])

    def test_rw_multiprocess(self) -> None:
        new_labelss = []
        for i in range(20):
            new_labelss.append([f"{i}-{j}" for j in range(10)])
        args = list(zip([self._label_storage_file] * len(new_labelss), new_labelss))
        with mp.Pool(7) as p:
            p.map(_test_rw, args)
        cim = load_or_create_userlabels(label_storage_file=self._label_storage_file)
        for nls in new_labelss:
            for nl in nls:
                try:
                    self.assertTrue(cim.has_name(nl))
                except AssertionError as e:
                    breakpoint()
                    raise e


def _test_rw(args: list) -> None:
    label_storage_file: str = args[0]
    new_labels: list = args[1]
    cim = load_or_create_userlabels(label_storage_file=label_storage_file)
    cim.add_main_names(new_labels)
