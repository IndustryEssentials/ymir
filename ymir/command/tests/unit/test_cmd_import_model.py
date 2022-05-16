import os
import shutil
import tarfile
import unittest

import yaml

from mir.commands.model_importing import CmdModelImport
from mir.tools import mir_storage_ops, settings as mir_settings, utils as mir_utils
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdImportModel(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._src_model_root = os.path.join(self._test_root, 'src_model')
        self._src_model_package_path = os.path.join(self._src_model_root, 'model.tar.gz')
        self._assets_location = os.path.join(self._test_root, "assets")
        self._models_location = os.path.join(self._test_root, "models")
        self._working_root = os.path.join(self._test_root, "work")
        self._mir_root = os.path.join(self._test_root, "mir-root")

    def setUp(self) -> None:
        self._prepare_dirs()
        self._prepare_model()
        self._prepare_mir_repo()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['cat', 'person'])
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._assets_location, exist_ok=True)
        os.makedirs(self._models_location, exist_ok=True)
        os.makedirs(self._working_root, exist_ok=True)
        os.makedirs(self._mir_root, exist_ok=True)
        os.makedirs(self._src_model_root, exist_ok=True)

    def _deprepare_dirs(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def _prepare_model(self):
        with open(os.path.join(self._src_model_root, 'best.weights'), 'w') as f:
            f.write('fake darknet weights model')
        # note: unknown-car is not in user labels, we still expect it success
        model_storage = mir_utils.ModelStorage(models=['best.weights'],
                                               executor_config={'class_names': ['cat', 'person', 'unknown-car']},
                                               task_context={
                                                   mir_settings.PRODUCER_KEY: mir_settings.PRODUCER_NAME,
                                                   'mAP': 0.5
                                               })
        with open(os.path.join(self._src_model_root, 'ymir-info.yaml'), 'w') as f:
            yaml.safe_dump(model_storage.as_dict(), f)
        with tarfile.open(self._src_model_package_path, 'w:gz') as tar_gz_f:
            tar_gz_f.add(os.path.join(self._src_model_root, 'best.weights'), 'best.weights')
            tar_gz_f.add(os.path.join(self._src_model_root, 'ymir-info.yaml'), 'ymir-info.yaml')

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)

    # protected: check result
    def _check_result(self):
        """ check destination model package file """
        model = mir_storage_ops.MirStorageOps.load_single_model(mir_root=self._mir_root,
                                                                mir_branch='a',
                                                                mir_task_id='a')
        self.assertTrue(os.path.isfile(os.path.join(self._models_location, model['model_hash'])))

    # public: test cases
    def test_00(self):
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.package_path = self._src_model_package_path
        fake_args.dst_rev = 'a@a'
        fake_args.model_location = self._models_location
        fake_args.work_dir = self._working_root
        instance = CmdModelImport(fake_args)
        cmd_run_result = instance.run()

        self.assertEqual(MirCode.RC_OK, cmd_run_result)
        self._check_result()
