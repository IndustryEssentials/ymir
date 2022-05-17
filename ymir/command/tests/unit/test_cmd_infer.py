import json
import os
import shutil
import tarfile
import unittest
from unittest import mock

import yaml

from mir.commands.infer import CmdInfer
from mir.tools import settings as mir_settings, utils as mir_utils
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdInfer(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._mir_repo_root = os.path.join(self._test_root, 'mir-demo-repo')
        self._models_location = os.path.join(self._test_root, 'models')
        self._src_assets_root = os.path.join(self._test_root, 'assets')  # source assets, index and infer config file
        self._working_root = os.path.join(self._test_root, 'work')  # work directory for cmd infer
        self._config_file = os.path.join(self._test_root, 'config.yaml')
        self._assets_index_file = os.path.join(self._src_assets_root, 'index.tsv')

    def setUp(self) -> None:
        self._prepare_dir()
        self._prepare_mir_root()
        self._prepare_assets()
        self._prepare_model()
        self._prepare_config_file()
        self._prepare_infer_result_file()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dir()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dir(self):
        os.makedirs(self._test_root, exist_ok=True)
        os.makedirs(self._models_location, exist_ok=True)
        os.makedirs(self._working_root, exist_ok=True)
        os.makedirs(os.path.join(self._working_root, 'out'), exist_ok=True)
        os.makedirs(self._src_assets_root, exist_ok=True)

    def _deprepare_dir(self):
        shutil.rmtree(self._test_root)

    def _prepare_mir_root(self):
        test_utils.mir_repo_init(self._mir_repo_root)
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['person', 'cat'])

    def _prepare_assets(self):
        test_assets_root = TestCmdInfer._test_assets_root()
        shutil.copyfile(src=os.path.join(test_assets_root, '2007_000032.jpg'),
                        dst=os.path.join(self._working_root, '2007_000032.jpg'))
        with open(self._assets_index_file, 'w') as f:
            f.write(f'{self._working_root}/2007_000032.jpg\n')

    def _prepare_model(self):
        # model params
        with open(os.path.join(self._models_location, 'model.params'), 'w') as f:
            f.write('fake model params')

        # model json
        with open(os.path.join(self._models_location, 'model.json'), 'w') as f:
            f.write('fake model json')

        # model config
        test_assets_root = TestCmdInfer._test_assets_root()
        with open(os.path.join(test_assets_root, 'training-template.yaml'), 'r') as f:
            training_config = yaml.safe_load(f.read())

        training_config['anchors'] = '12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401'
        training_config['class_names'] = ['person', 'cat', 'unknown-car']

        model_storage = mir_utils.ModelStorage(models=['model.params', 'model.json'],
                                               executor_config=training_config,
                                               task_context={
                                                   'src_revs': 'master',
                                                   'dst_rev': 'a'
                                               })

        with open(os.path.join(self._models_location, 'ymir-info.yaml'), 'w') as f:
            yaml.dump(model_storage.as_dict(), f)

        # pack model
        with tarfile.open(os.path.join(self._models_location, 'fake_model_hash'), "w:gz") as dest_tar_gz:
            dest_tar_gz.add(os.path.join(self._models_location, 'model.params'), 'model.params')
            dest_tar_gz.add(os.path.join(self._models_location, 'model.json'), 'model.json')
            dest_tar_gz.add(os.path.join(self._models_location, 'ymir-info.yaml'), 'ymir-info.yaml')

    def _prepare_config_file(self):
        test_assets_root = TestCmdInfer._test_assets_root()
        # shutil.copyfile(src=os.path.join(test_assets_root, 'infer-template.yaml'), dst=self._config_file)
        with open(os.path.join(test_assets_root, 'infer-template.yaml'), 'r') as f:
            executor_config = yaml.safe_load(f)
        with open(self._config_file, 'w') as f:
            yaml.safe_dump({mir_settings.EXECUTOR_CONFIG_KEY: executor_config}, f)
            
    def _prepare_infer_result_file(self):
        fake_infer_output_dict = {
            'detection': {
                '2007_000032.jpg': {
                    'annotations': [
                        {
                            'box': {
                                'x': 0,
                                'y': 0,
                                'w': 30,
                                'h': 30
                            },
                            'score': 0.5,
                            'class_name': 'cat',
                        },
                    ],
                },
            },
        }
        infer_output_file = os.path.join(self._working_root, 'out', 'infer-result.json')
        with open(infer_output_file, 'w') as f:
            f.write(json.dumps(fake_infer_output_dict))

    @staticmethod
    def _test_assets_root() -> str:
        return os.path.join(os.path.dirname(__file__), '..', 'assets')

    # protected: mocked functions
    def _mock_run_docker_cmd(*args, **kwargs):
        pass

    # public: test cases
    @mock.patch('subprocess.run', side_effect=_mock_run_docker_cmd)
    def test_00(self, mock_run):
        fake_args = type('', (), {})()
        fake_args.work_dir = self._working_root
        fake_args.mir_root = self._mir_repo_root
        fake_args.model_location = self._models_location
        fake_args.model_hash = 'fake_model_hash'
        fake_args.index_file = self._assets_index_file
        fake_args.config_file = self._config_file
        fake_args.executor = 'infer-executor:fake'
        fake_args.executant_name = 'executor-instance'
        cmd_instance = CmdInfer(fake_args)
        cmd_result = cmd_instance.run()

        # check running result
        self.assertEqual(MirCode.RC_OK, cmd_result)

        expected_cmd = ['nvidia-docker', 'run', '--rm']
        expected_cmd.append(f"-v{fake_args.work_dir}:/in/assets:ro")
        expected_cmd.append(f"-v{os.path.join(fake_args.work_dir, 'in', 'models')}:/in/models:ro")
        expected_cmd.append(
            f"-v{os.path.join(fake_args.work_dir, 'in', 'candidate-index.tsv')}:/in/candidate-index.tsv")
        expected_cmd.append(f"-v{os.path.join(fake_args.work_dir, 'in', 'config.yaml')}:/in/config.yaml")
        expected_cmd.append(f"-v{os.path.join(fake_args.work_dir, 'in', 'env.yaml')}:/in/env.yaml")
        expected_cmd.append(f"-v{os.path.join(fake_args.work_dir, 'out')}:/out")
        expected_cmd.extend(['--user', f"{os.getuid()}:{os.getgid()}"])
        expected_cmd.extend(['--name', fake_args.executant_name])
        expected_cmd.append(fake_args.executor)
        mock_run.assert_called_once_with(expected_cmd, check=True, stdout=mock.ANY, stderr=mock.ANY, text=True)

        # check assets and index.tsv
        with open(os.path.join(fake_args.work_dir, 'in', 'candidate-index.tsv'), 'r') as f:
            contents = f.read().splitlines()
            self.assertEqual(1, len(contents))
            self.assertEqual('/in/assets/2007_000032.jpg', contents[0])

        # check config
        with open(os.path.join(fake_args.work_dir, 'in', 'config.yaml'), 'r') as f:
            infer_config = yaml.safe_load(f.read())
            self.assertTrue('class_names' in infer_config)
            self.assertTrue('model_params_path' in infer_config)

        # check model params
        self.assertTrue(os.path.isfile(os.path.join(fake_args.work_dir, 'in', 'models', 'model.params')))
