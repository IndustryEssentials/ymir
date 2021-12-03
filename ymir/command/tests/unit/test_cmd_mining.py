import logging
import os
import shutil
import tarfile
import unittest
from unittest import mock

from google.protobuf.json_format import ParseDict
import yaml

from mir.commands.mining import CmdMining
import tests.utils as test_utils
import mir.protos.mir_command_pb2 as mirpb


class TestMiningCmd(unittest.TestCase):
    _USER_NAME = "test_user"
    _MIR_REPO_NAME = "ymir-dvc-test"
    _STORAGE_NAME = "monitor_storage_root"

    # lifecycle
    def __init__(self, methodName: str) -> None:
        # dir structure:
        # test_invoker_mining_sandbox_root
        # ├── monitor_storage_root
        # └── test_user
        #     └── ymir-dvc-test
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
        return 0

    # protected: custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _prepare_config(self):
        shutil.copyfile('tests/assets/mining-template.yaml', self._config_file)

    def _prepare_mir_repo(self):
        # init repo
        logging.info(f"mir repo: {self._mir_repo_root}")
        test_utils.mir_repo_init(self._mir_repo_root)
        # prepare branch a
        test_utils.mir_repo_create_branch(self._mir_repo_root, "a")
        self._prepare_mir_repo_branch_mining()

    def _prepare_mir_repo_branch_mining(self):
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_metadatas = mirpb.MirMetadatas()
        mir_tasks = mirpb.MirTasks()

        mock_image_file = os.path.join(self._storage_root, 'd4e4a60147f1e35bc7f5bc89284aa16073b043c9')
        shutil.copyfile("tests/assets/2007_000032.jpg", mock_image_file)
        mock_image_file = os.path.join(self._storage_root, 'a3008c032eb11c8d9ffcb58208a36682ee40900f')
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

        dict_tasks = {
            'tasks': {
                '5928508c-1bc0-43dc-a094-0352079e39b5': {
                    'type': 'TaskTypeMining',
                    'name': 'mining',
                    'task_id': 'mining-task-id',
                    'timestamp': '1624376173'
                }
            },
            'head_task_id': '5928508c-1bc0-43dc-a094-0352079e39b5',
        }
        ParseDict(dict_tasks, mir_tasks)

        print("self._mir_repo_root: ", self._mir_repo_root)
        test_utils.mir_repo_commit_all(self._mir_repo_root, mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
                                       "prepare_branch_mining")

    # public: test cases
    @mock.patch("mir.commands.infer.CmdInfer.run_with_args", side_effect=_mock_run_func)
    def test_mining_cmd_00(self, mock_run):
        self._prepare_dirs()
        self._prepare_config()
        self._prepare_mir_repo()

        args = type('', (), {})()
        args.src_revs = 'a@5928508c-1bc0-43dc-a094-0352079e39b5'
        args.dst_rev = 'a@mining-task-id'
        args.model_hash = 'xyz'
        args.work_dir = os.path.join(self._storage_root, "mining-task-id")
        args.media_cache = ''
        args.model_location = self._storage_root
        args.media_location = self._storage_root
        args.topk = 1
        args.add_annotations = False
        args.mir_root = self._mir_repo_root
        args.config_file = self._config_file
        args.executor = 'al:0.0.1'
        args.executor_instance = 'executor-instance'
        mining_instance = CmdMining(args)
        mining_instance.run()

        mock_run.assert_called_once_with(work_dir=args.work_dir,
                                         media_path=os.path.join(args.work_dir, 'in', 'candidate'),
                                         model_location=args.model_location,
                                         model_hash=args.model_hash,
                                         index_file=os.path.join(args.work_dir, 'in', 'candidate', 'src-index.tsv'),
                                         config_file=args.config_file,
                                         task_id='mining-task-id',
                                         shm_size='16G',
                                         executor=args.executor,
                                         executor_instance=args.executor_instance,
                                         run_infer=False,
                                         run_mining=True)

        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
