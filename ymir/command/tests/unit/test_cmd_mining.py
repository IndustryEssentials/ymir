import logging
import os
import shutil
import tarfile
import time
import unittest
from unittest import mock

from google.protobuf.json_format import ParseDict
from mir.version import YMIR_VERSION, ymir_model_salient_version
import yaml

from mir.commands.mining import CmdMining
from mir.tools import mir_storage_ops, models, settings as mir_settings, mir_storage
from mir.tools.annotations import make_empty_mir_annotations
from mir.tools.class_ids import ids_file_path
import mir.protos.mir_command_pb2 as mirpb
import tests.utils as test_utils


class TestMiningCmd(unittest.TestCase):
    _USER_NAME = "test_user"
    _MIR_REPO_NAME = "mir-test-repo"
    _STORAGE_NAME = "monitor_storage_root"

    # lifecycle
    def __init__(self, methodName: str) -> None:
        # dir structure:
        # test_invoker_mining_sandbox_root
        # ├── monitor_storage_root
        # └── test_user
        #     └── mir-test-repo
        super().__init__(methodName=methodName)
        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._USER_NAME)
        self._mir_repo_root = os.path.join(self._user_root, self._MIR_REPO_NAME)
        self._storage_root = os.path.join(self._sandbox_root, self._STORAGE_NAME)
        self._config_file = os.path.join(self._sandbox_root, 'config.yaml')

    def setUp(self) -> None:
        test_utils.check_commands()

    def tearDown(self) -> None:
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        return super().tearDown()

    # protected: mock functions
    def _mock_run_func(*args, **kwargs):
        output_file = os.path.join(kwargs['work_dir'], 'out', 'result.tsv')
        with open(output_file, 'w') as f:
            f.writelines("d4e4a60147f1e35bc7f5bc89284aa16073b043c9\t0.1")

        # a fake prediction result file
        prediction = mirpb.SingleTaskAnnotations()
        with open(os.path.join(kwargs['work_dir'], 'out', 'prediction.mir'), 'wb') as f:
            f.write(prediction.SerializeToString())

        return 0

    def _mock_prepare_model(*args, **kwargs):
        mss = models.ModelStageStorage(stage_name='default', files=['0.params'], mAP=0.5, timestamp=int(time.time()))
        ms = models.ModelStorage(executor_config={'class_names': ['person', 'cat', 'unknown-car']},
                                 task_context={'task_id': '0'},
                                 stages={mss.stage_name: mss},
                                 best_stage_name=mss.stage_name,
                                 model_hash='xyz',
                                 stage_name=mss.stage_name,
                                 object_type=mirpb.ObjectType.OT_DET_BOX,
                                 package_version=ymir_model_salient_version(YMIR_VERSION))
        return ms

    # protected: custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _prepare_config(self):
        with open('tests/assets/mining-template.yaml', 'r') as f:
            config = yaml.safe_load(f)
        with open(self._config_file, 'w') as f:
            yaml.safe_dump({mir_settings.EXECUTOR_CONFIG_KEY: config}, f)

    def _prepare_mir_repo(self):
        # init repo
        logging.info(f"mir repo: {self._mir_repo_root}")
        test_utils.mir_repo_init(self._mir_repo_root)
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['person', 'cat'])
        # prepare branch a
        test_utils.mir_repo_create_branch(self._mir_repo_root, "a")
        self._prepare_mir_repo_branch_mining()

    def _prepare_mir_repo_branch_mining(self):
        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = make_empty_mir_annotations()

        mock_image_file = mir_storage.get_asset_storage_path(self._storage_root,
                                                             'd4e4a60147f1e35bc7f5bc89284aa16073b043c9')
        shutil.copyfile("tests/assets/2007_000032.jpg", mock_image_file)
        mock_image_file = mir_storage.get_asset_storage_path(self._storage_root,
                                                             'a3008c032eb11c8d9ffcb58208a36682ee40900f')
        shutil.copyfile("tests/assets/2007_000243.jpg", mock_image_file)

        mock_training_config_file = os.path.join(self._storage_root, 'config.yaml')
        shutil.copyfile('tests/assets/training-template.yaml', mock_training_config_file)

        mock_model_json = os.path.join(self._storage_root, '1.json')
        with open(mock_model_json, 'w') as f:
            f.writelines("mock")
        mock_model_params = os.path.join(self._storage_root, '1.params')
        with open(mock_model_params, 'w') as f:
            f.writelines("mock")
        with open(mock_training_config_file, 'r') as f:
            config = yaml.safe_load(f.read())
        config['class_names'] = ['cat', 'person']
        with open(mock_training_config_file, 'w') as f:
            yaml.dump(config, f)
        mock_model_file = os.path.join(self._storage_root, 'xyz')
        with tarfile.open(mock_model_file, "w:gz") as dest_tar_gz:
            dest_tar_gz.add(mock_model_json, os.path.basename(mock_model_json))
            dest_tar_gz.add(mock_model_params, os.path.basename(mock_model_params))
            dest_tar_gz.add(mock_training_config_file, os.path.basename(mock_training_config_file))

        dict_metadatas = {
            'attributes': {
                'd4e4a60147f1e35bc7f5bc89284aa16073b043c9': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
            }
        }
        ParseDict(dict_metadatas, mir_metadatas)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeMining,
                                           task_id='5928508c-1bc0-43dc-a094-0352079e39b5',
                                           message='prepare_branch_mining')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_repo_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    # public: test cases
    @mock.patch("mir.commands.infer.CmdInfer.run_with_args", side_effect=_mock_run_func)
    @mock.patch("mir.tools.models.prepare_model", side_effect=_mock_prepare_model)
    def test_mining_cmd_00(self, mock_prepare, mock_run):
        self._prepare_dirs()
        self._prepare_config()
        self._prepare_mir_repo()

        args = type('', (), {})()
        args.src_revs = 'a@5928508c-1bc0-43dc-a094-0352079e39b5'
        args.strategy = 'host'
        args.dst_rev = 'a@mining-task-id'
        args.model_hash_stage = 'xyz@default'
        args.work_dir = os.path.join(self._storage_root, "mining-task-id")
        args.asset_cache_dir = ''
        args.model_location = self._storage_root
        args.media_location = self._storage_root
        args.topk = 1
        args.add_prediction = True
        args.mir_root = self._mir_repo_root
        args.label_storage_file = ids_file_path(self._mir_repo_root)
        args.config_file = self._config_file
        args.executor = 'al:0.0.1'
        args.executant_name = 'executor-instance'
        args.run_as_root = False
        mining_instance = CmdMining(args)
        mining_instance.run()

        expected_model_storage = TestMiningCmd._mock_prepare_model()
        mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=self._mir_repo_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms=mirpb.MirStorage.MIR_ANNOTATIONS,
            as_dict=False)
        self.assertEqual({0, 1}, set(mir_annotations.prediction.eval_class_ids))
        # dont care about timestamp
        expected_model_storage.stages['default'].timestamp = mir_annotations.prediction.model.stages[
            'default'].timestamp
        self.assertEqual(expected_model_storage.get_model_meta(), mir_annotations.prediction.model)
        mock_run.assert_called_once_with(work_dir=args.work_dir,
                                         label_storage_file=args.label_storage_file,
                                         media_path=os.path.join(args.work_dir, 'in', 'assets'),
                                         model_storage=expected_model_storage,
                                         index_file=os.path.join(args.work_dir, 'in', 'candidate-src-index.tsv'),
                                         config_file=args.config_file,
                                         task_id='mining-task-id',
                                         executor=args.executor,
                                         executant_name=args.executant_name,
                                         run_as_root=args.run_as_root,
                                         run_infer=args.add_prediction,
                                         run_mining=True)

        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
