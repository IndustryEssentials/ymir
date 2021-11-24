import os
import shutil
import tarfile
import unittest
from unittest import mock

import yaml

from mir.commands.infer import CmdInfer
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdInfer(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._models_location = os.path.join(self._test_root, 'models')
        self._src_assets_root = os.path.join(self._test_root, 'assets')  # source assets, index and infer config file
        self._working_root = os.path.join(self._test_root, 'work')  # work directory for cmd infer
        self._config_file = os.path.join(self._test_root, 'config.yaml')
        self._assets_index_file = os.path.join(self._src_assets_root, 'index.tsv')

    def setUp(self) -> None:
        self._prepare_dir()
        self._prepare_assets()
        self._prepare_model()
        self._prepare_config_file()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dir()
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dir(self):
        os.makedirs(self._test_root, exist_ok=True)
        os.makedirs(self._models_location, exist_ok=True)
        os.makedirs(self._working_root, exist_ok=True)
        os.makedirs(self._src_assets_root, exist_ok=True)

    def _deprepare_dir(self):
        shutil.rmtree(self._test_root)

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
        training_config['class_names'] = ['person', 'cat']

        with open(os.path.join(self._models_location, 'config.yaml'), 'w') as f:
            yaml.dump(training_config, f)

        # pack model
        with tarfile.open(os.path.join(self._models_location, 'fake_model_hash'), "w:gz") as dest_tar_gz:
            dest_tar_gz.add(os.path.join(self._models_location, 'model.params'), 'model.params')
            dest_tar_gz.add(os.path.join(self._models_location, 'model.json'), 'model.json')
            dest_tar_gz.add(os.path.join(self._models_location, 'config.yaml'), 'config.yaml')

    def _prepare_config_file(self):
        test_assets_root = TestCmdInfer._test_assets_root()
        shutil.copyfile(src=os.path.join(test_assets_root, 'infer-template.yaml'), dst=self._config_file)

    @staticmethod
    def _test_assets_root() -> str:
        return os.path.join(os.path.dirname(__file__), '..', 'assets')

    # protected: mocked functions
    def _mock_run_docker_cmd(*args, **kwargs):
        pass

    def _mock_process_results(*args, **kwargs):
        pass

    # public: test cases
    @mock.patch('mir.commands.infer.run_docker_cmd', side_effect=_mock_run_docker_cmd)
    @mock.patch('mir.commands.infer._process_infer_results', side_effect=_mock_process_results)
    def test_00(self, mock_process, mock_run):
        fake_args = type('', (), {})()
        fake_args.work_dir = self._working_root
        fake_args.model_location = self._models_location
        fake_args.model_hash = 'fake_model_hash'
        fake_args.index_file = self._assets_index_file
        fake_args.config_file = self._config_file
        fake_args.executor = 'infer-executor:fake'
        fake_args.executor_name = 'executor-name'
        cmd_instance = CmdInfer(fake_args)
        cmd_result = cmd_instance.run()

        # check running result
        self.assertEqual(MirCode.RC_OK, cmd_result)
        mock_run.assert_called_once_with(asset_path=fake_args.work_dir,
                                         index_file_path=os.path.join(fake_args.work_dir, 'in', 'candidate',
                                                                      'index.tsv'),
                                         model_path=os.path.join(fake_args.work_dir, 'in', 'model'),
                                         config_file_path=os.path.join(fake_args.work_dir, 'in', 'config.yaml'),
                                         out_path=os.path.join(fake_args.work_dir, 'out'),
                                         executor=fake_args.executor,
                                         executor_name=fake_args.executor_name,
                                         shm_size=None,
                                         task_type=mock.ANY)
        mock_process.assert_called_once_with(infer_result_file=os.path.join(fake_args.work_dir, 'out',
                                                                            'infer-result.json'),
                                             max_boxes=50)

        # check assets and index.tsv
        with open(os.path.join(fake_args.work_dir, 'in', 'candidate', 'index.tsv'), 'r') as f:
            contents = f.read().splitlines()
            self.assertEqual(1, len(contents))
            self.assertEqual('/in/candidate/2007_000032.jpg', contents[0])

        # check config
        with open(os.path.join(fake_args.work_dir, 'in', 'config.yaml'), 'r') as f:
            infer_config = yaml.safe_load(f.read())
            self.assertTrue('class_names' in infer_config)
            self.assertTrue('model_params_path' in infer_config)

        # check model params
        self.assertTrue(os.path.isfile(os.path.join(fake_args.work_dir, 'in', 'model', 'model.params')))
