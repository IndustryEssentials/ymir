import os
import shutil
import tarfile
import time
import unittest

import yaml

from mir.commands.import_model import CmdModelImport
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, models, settings as mir_settings
from mir.tools.code import MirCode
from mir.version import YMIR_MODEL_VERSION
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
        mss = models.ModelStageStorage(stage_name='default_best_stage',
                                       files=['best.weights'],
                                       mAP=0.5,
                                       timestamp=int(time.time()))
        model_storage = models.ModelStorage(executor_config={'class_names': ['cat', 'person', 'unknown-car']},
                                            task_context={
                                                mir_settings.PRODUCER_KEY: mir_settings.PRODUCER_NAME,
                                                'mAP': 0.5
                                            },
                                            stages={mss.stage_name: mss},
                                            best_stage_name=mss.stage_name,
                                            object_type=mirpb.ObjectType.OT_UNKNOWN,  # will be treated as detection
                                            package_version=YMIR_MODEL_VERSION)
        with open(os.path.join(self._src_model_root, 'ymir-info.yaml'), 'w') as f:
            yaml.safe_dump(model_storage.dict(), f)
        with tarfile.open(self._src_model_package_path, 'w:gz') as tar_gz_f:
            tar_gz_f.add(os.path.join(self._src_model_root, 'best.weights'), f"{mss.stage_name}/best.weights")
            tar_gz_f.add(os.path.join(self._src_model_root, 'ymir-info.yaml'), 'ymir-info.yaml')

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)

    # protected: check result
    def _check_result(self):
        """ check destination model package file """
        mir_storage_data: mirpb.MirTasks = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=self._mir_root, mir_branch='a', ms=mirpb.MirStorage.MIR_TASKS, mir_task_id='a')
        task = mir_storage_data.tasks[mir_storage_data.head_task_id]
        self.assertTrue(os.path.isfile(os.path.join(self._models_location, task.model.model_hash)))
        self.assertEqual(task.model.object_type, mirpb.ObjectType.OT_DET_BOX)

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
