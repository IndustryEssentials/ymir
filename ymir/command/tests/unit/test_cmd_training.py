import os
import shutil
from typing import List, Tuple
import unittest
from unittest import mock

from google.protobuf import json_format
from mir.tools.errors import MirRuntimeError
import yaml

from mir.commands import training
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import hash_utils, mir_repo_utils, mir_storage_ops, settings as mir_settings, utils as mir_utils
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdTraining(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._assets_location = os.path.join(self._test_root, "assets")
        self._models_location = os.path.join(self._test_root, "models")
        self._working_root = os.path.join(self._test_root, "work")
        self._mir_root = os.path.join(self._test_root, "mir-root")
        self._config_file = os.path.join(self._test_root, 'config.yaml')

    def setUp(self) -> None:
        self.__prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['freshbee', 'person', 'airplane,aeroplane'])
        self.__prepare_assets()
        self.__prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dirs()
        return super().tearDown()

    # private: prepare env
    def __prepare_dirs(self):
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._assets_location)
        test_utils.remake_dirs(self._models_location)
        test_utils.remake_dirs(self._mir_root)
        test_utils.remake_dirs(self._working_root)
        
    def __prepare_mir_repo(self):
        self.__prepare_mir_repo_branch_a()
        self.__prepare_mir_repo_branch_b()

    def __prepare_mir_repo_branch_a(self):
        """
        creates mir repo, assumes that `self._mir_root` already created
        """
        test_utils.mir_repo_init(self._mir_root)
        test_utils.mir_repo_create_branch(self._mir_root, "a")

        # metadatas
        metadatas_dict = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeTraining',
                    'width': 500,
                    'height': 281,
                    'imageChannels': 3
                },
                "a3008c032eb11c8d9ffcb58208a36682ee40900f": {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeValidation',
                    'width': 500,
                    'height': 333,
                    'imageChannels': 3
                }
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        # annotations
        annotations_dict = {
            "task_annotations": {
                "a": {
                    "image_annotations": {
                        "430df22960b0f369318705800139fcc8ec38a3e4": {
                            "annotations": [{
                                "index": 0,
                                "box": {
                                    "x": 104,
                                    "y": 78,
                                    "w": 272,
                                    "h": 105
                                },
                                "class_id": 3,
                                "score": 1,
                            }, {
                                "index": 1,
                                "box": {
                                    "x": 133,
                                    "y": 88,
                                    "w": 65,
                                    "h": 36
                                },
                                "class_id": 3,
                                "score": 1,
                            }, {
                                "index": 2,
                                "box": {
                                    "x": 195,
                                    "y": 180,
                                    "w": 19,
                                    "h": 50
                                },
                                "class_id": 2,
                                "score": 1,
                            }, {
                                "index": 3,
                                "box": {
                                    "x": 26,
                                    "y": 189,
                                    "w": 19,
                                    "h": 95
                                },
                                "class_id": 2,
                                "score": 1,
                            }]
                        },
                        "a3008c032eb11c8d9ffcb58208a36682ee40900f": {
                            "annotations": [{
                                "index": 0,
                                "box": {
                                    "x": 181,
                                    "y": 127,
                                    "w": 94,
                                    "h": 67
                                },
                                "class_id": 3,
                                "score": 1,
                            }]
                        },
                    }
                }
            },
            'head_task_id': 'a'
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        # save and commit
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='a', message='import')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    def __prepare_mir_repo_branch_b(self):
        # a@b: no training set
        # metadatas
        metadatas_dict = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeValidation',
                    'width': 500,
                    'height': 281,
                    'imageChannels': 3
                },
                "a3008c032eb11c8d9ffcb58208a36682ee40900f": {
                    'assetType': 'AssetTypeImageJpeg',
                    'tvtType': 'TvtTypeValidation',
                    'width': 500,
                    'height': 333,
                    'imageChannels': 3
                }
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        # save and commit
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='b', message='import')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations(),
                                                      },
                                                      task=task)

    def __prepare_assets(self):
        """
        copy all assets from project to assets_location, assumes that `self._assets_location` already created
        """
        image_paths = ["tests/assets/2007_000032.jpg", "tests/assets/2007_000243.jpg"]
        sha1sum_path_pairs = [(hash_utils.sha1sum_for_file(image_path), image_path)
                              for image_path in image_paths]  # type: List[Tuple[str, str]]
        for sha1sum, image_path in sha1sum_path_pairs:
            shutil.copyfile(image_path, os.path.join(self._assets_location, sha1sum))

        shutil.copyfile('tests/assets/training-template.yaml', self._config_file)
        with open(self._config_file, 'r') as f:
            executor_config = yaml.safe_load(f.read())
        executor_config['class_names'] = ['airplane']
        executor_config['gpu_id'] = '0'
        config = {mir_settings.EXECUTOR_CONFIG_KEY: executor_config}
        with open(self._config_file, 'w') as f:
            yaml.dump(config, f)

    def __deprepare_dirs(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    # private: mocks
    def __mock_run_train_cmd(*args, **kwargs):
        return MirCode.RC_OK

    def __mock_process_model_storage(*args, **kwargs):
        return ("xyz", 0.9)

    # public: test cases
    @mock.patch("mir.commands.training._run_train_cmd", side_effect=__mock_run_train_cmd)
    @mock.patch("mir.commands.training._process_model_storage", side_effect=__mock_process_model_storage)
    def test_normal_00(self, *mock_run):
        """ normal case """
        fake_args = type('', (), {})()
        fake_args.src_revs = "a@a"
        fake_args.dst_rev = "a@test_training_cmd"
        fake_args.mir_root = self._mir_root
        fake_args.model_path = self._models_location
        fake_args.media_location = self._assets_location
        fake_args.model_hash = ''
        fake_args.work_dir = self._working_root
        fake_args.force = True
        fake_args.force_rebuild = False
        fake_args.executor = "executor"
        fake_args.executant_name = 'executor-instance'
        fake_args.tensorboard_dir = ''
        fake_args.config_file = self._config_file
        fake_args.asset_cache_dir = ''

        cmd = training.CmdTrain(fake_args)
        cmd_run_result = cmd.run()

        # check result
        self.assertEqual(MirCode.RC_OK, cmd_run_result)

    def test_abnormal_00(self):
        """ no training set """
        fake_args = type('', (), {})()
        fake_args.src_revs = "a@b"
        fake_args.dst_rev = "b@test_training_cmd"
        fake_args.mir_root = self._mir_root
        fake_args.model_path = self._models_location
        fake_args.media_location = self._assets_location
        fake_args.model_hash = ''
        fake_args.work_dir = self._working_root
        fake_args.force = True
        fake_args.force_rebuild = False
        fake_args.executor = "executor"
        fake_args.executant_name = 'executor-instance'
        fake_args.tensorboard_dir = ''
        fake_args.config_file = self._config_file
        fake_args.asset_cache_dir = ''

        cmd = training.CmdTrain(fake_args)
        with self.assertRaises(MirRuntimeError):
            cmd_run_result = cmd.run()
        self.assertTrue(mir_repo_utils.mir_check_branch_exists(self._mir_root, 'b@test_training_cmd'))
