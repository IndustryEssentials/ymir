import os
import shutil
from typing import Dict, List, Tuple
import unittest
from unittest import mock

from google.protobuf import json_format

from mir.commands import exporting
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import data_exporter, hash_utils
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdExport(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._assets_location = os.path.join(self._test_root, 'assets_location')
        self._dest_root = os.path.join(self._test_root, 'export_dest')
        self._mir_root = os.path.join(self._test_root, 'mir-repo')

    def setUp(self) -> None:
        self.__prepare_dirs()
        self.__prepare_mir_repo()
        self.__prepare_assets()
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dirs()
        return super().tearDown()

    # private: prepare env
    def __prepare_dirs(self):
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._assets_location)
        test_utils.remake_dirs(self._dest_root)
        test_utils.remake_dirs(self._mir_root)

    def __deprepare_dirs(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def __prepare_assets(self):
        '''
        copy all assets from project to assets_location, assumes that `self._assets_location` already created
        '''
        image_paths = ['tests/assets/2007_000032.jpg', 'tests/assets/2007_000243.jpg']
        sha1sum_path_pairs = [(hash_utils.sha1sum_for_file(image_path), image_path)
                              for image_path in image_paths]  # type: List[Tuple[str, str]]
        for sha1sum, image_path in sha1sum_path_pairs:
            shutil.copyfile(image_path, os.path.join(self._assets_location, sha1sum))

    def __prepare_mir_repo(self):
        '''
        creates mir repo, assumes that `self._mir_root` already created
        '''
        test_utils.mir_repo_init(self._mir_root)
        test_utils.mir_repo_create_branch(self._mir_root, 'a')

        # metadatas
        metadatas_dict = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 281,
                    'imageChannels': 3
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'assetType': 'AssetTypeImageJpeg',
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
            'task_annotations': {
                'a': {
                    'image_annotations': {
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 104,
                                    'y': 78,
                                    'w': 272,
                                    'h': 105
                                },
                                'class_id': 52,
                                'score': 1,
                            }, {
                                'index': 1,
                                'box': {
                                    'x': 133,
                                    'y': 88,
                                    'w': 65,
                                    'h': 36
                                },
                                'class_id': 52,
                                'score': 1,
                            }, {
                                'index': 2,
                                'box': {
                                    'x': 195,
                                    'y': 180,
                                    'w': 19,
                                    'h': 50
                                },
                                'class_id': 2,
                                'score': 1,
                            }, {
                                'index': 3,
                                'box': {
                                    'x': 26,
                                    'y': 189,
                                    'w': 19,
                                    'h': 95
                                },
                                'class_id': 2,
                                'score': 1,
                            }]
                        },
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'annotations': [{
                                'index': 0,
                                'box': {
                                    'x': 181,
                                    'y': 127,
                                    'w': 94,
                                    'h': 67
                                },
                                'class_id': 52,
                                'score': 1,
                            }]
                        },
                    }
                }
            }
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        # keywords
        keywords_dict = {
            'keywords': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'predifined_keyids': [2, 52],
                    'customized_keywords': ['pascal']
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'predifined_keyids': [52],
                    'customized_keywords': ['pascal']
                },
            }
        }
        mir_keywords = mirpb.MirKeywords()
        json_format.ParseDict(keywords_dict, mir_keywords)

        # tasks
        tasks_dict = {
            'tasks': {
                'a': {
                    'type': 'TaskTypeImportData',
                    'name': 'import',
                    'task_id': 'a',
                    'timestamp': 17020362735,
                }
            }
        }
        mir_tasks = mirpb.MirTasks()
        json_format.ParseDict(tasks_dict, mir_tasks)

        # save and commit
        test_utils.mir_repo_commit_all(mir_root=self._mir_root,
                                       mir_metadatas=mir_metadatas,
                                       mir_annotations=mir_annotations,
                                       mir_tasks=mir_tasks,
                                       src_branch='master',
                                       dst_branch='a',
                                       task_id='a',
                                       no_space_message='test_tools_data_exporter_branch_a')

    # private: mocked
    def __mock_export(*args, **kwargs) -> Dict[str, Tuple[str, str]]:
        return {}

    # private: test cases
    @mock.patch('mir.tools.data_exporter.export', side_effect='__mock_export')
    def test_normal_00(self, mock_export):
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.asset_dir = self._dest_root
        fake_args.annotation_dir = self._dest_root
        fake_args.media_location = self._assets_location
        fake_args.src_revs = 'a@a'
        fake_args.format = 'voc'
        fake_args.work_dir = ''
        runner = exporting.CmdExport(fake_args)
        result = runner.run()
        self.assertEqual(MirCode.RC_OK, result)

        mock_export.assert_called_once_with(mir_root=self._mir_root,
                                            assets_location=self._assets_location,
                                            class_type_ids={},
                                            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4',
                                                       'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
                                            asset_dir=self._dest_root,
                                            annotation_dir=self._dest_root,
                                            need_ext=True,
                                            need_id_sub_folder=False,
                                            base_branch='a',
                                            base_task_id='a',  # see: fake_args.src_revs = 'a@a'
                                            format_type=data_exporter.ExportFormat.EXPORT_FORMAT_VOC)
