import os
import shutil
from typing import List, Tuple
import unittest

from google.protobuf import json_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import data_exporter, hash_utils
from tests import utils as test_utils


class TestArkDataExporter(unittest.TestCase):
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
        # self.__deprepare_dirs()
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
            },
            'head_task_id': 'a',
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
            },
            'head_task_id': 'a'
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

    # private: check result
    def __check_result(self, asset_ids, format_type, export_path, index_file_path):
        # check files
        for asset_id in asset_ids:
            asset_path = os.path.join(export_path, asset_id + '.jpeg')
            self.assertTrue(os.path.isfile(asset_path))
            if format_type == data_exporter.ExportFormat.EXPORT_FORMAT_ARK:
                annotation_path = os.path.join(export_path, asset_id + '.txt')
            elif format_type == data_exporter.ExportFormat.EXPORT_FORMAT_VOC:
                annotation_path = os.path.join(export_path, asset_id + '.xml')
            self.assertTrue(os.path.isfile(annotation_path))

        #   index file exists
        self.assertTrue(os.path.isfile(index_file_path))
        #   index file have enough lines
        #   and each line is accessable
        with open(index_file_path, 'r') as idx_f:
            lines = idx_f.readlines()
            self.assertEqual(len(lines), len(asset_ids))
            for line in lines:
                os.path.isfile(os.path.join(export_path, line))

    def __check_ark_annotations(self, asset_id: str, export_path: str, expected_first_two_cols: List[Tuple[int, int]]):
        annotation_path = os.path.join(export_path, asset_id + '.txt')
        with open(annotation_path, 'r') as f:
            lines = f.read().splitlines()
        self.assertEqual(len(expected_first_two_cols), len(lines))
        for line_idx, line in enumerate(lines):
            line_components = line.split(',')
            for col_idx in range(2):
                self.assertEqual(expected_first_two_cols[line_idx][col_idx], int(line_components[col_idx].strip()))

    # public: test cases
    def test_normal_00(self):
        ''' normal case: ark format '''
        asset_ids = {'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'}
        train_path = os.path.join(self._dest_root, 'train')

        data_exporter.export(mir_root=self._mir_root,
                             assets_location=self._assets_location,
                             class_type_ids={
                                 2: 0,
                                 52: 1
                             },
                             asset_ids=asset_ids,
                             asset_dir=train_path,
                             annotation_dir=train_path,
                             need_ext=True,
                             need_id_sub_folder=False,
                             base_branch='a',
                             base_task_id='a',
                             format_type=data_exporter.ExportFormat.EXPORT_FORMAT_ARK,
                             index_file_path=os.path.join(train_path, 'index.tsv'),
                             index_prefix=None)

        # check result
        self.__check_result(asset_ids=asset_ids,
                            format_type=data_exporter.ExportFormat.EXPORT_FORMAT_ARK,
                            export_path=train_path,
                            index_file_path=os.path.join(train_path, 'index.tsv'))
        self.__check_ark_annotations(asset_id='430df22960b0f369318705800139fcc8ec38a3e4',
                                     export_path=train_path,
                                     expected_first_two_cols=[(1, 104), (1, 133), (0, 195), (0, 26)])

    def test_normal_01(self):
        ''' normal case: voc format '''
        asset_ids = {'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'}
        train_path = os.path.join(self._dest_root, 'train')

        data_exporter.export(mir_root=self._mir_root,
                             assets_location=self._assets_location,
                             class_type_ids={
                                 2: 0,
                                 52: 1
                             },
                             asset_ids=asset_ids,
                             asset_dir=train_path,
                             annotation_dir=train_path,
                             need_ext=True,
                             need_id_sub_folder=False,
                             base_branch='a',
                             base_task_id='a',
                             format_type=data_exporter.ExportFormat.EXPORT_FORMAT_VOC,
                             index_file_path=os.path.join(train_path, 'index.tsv'),
                             index_prefix=None)

        # check result
        self.__check_result(asset_ids=asset_ids,
                            format_type=data_exporter.ExportFormat.EXPORT_FORMAT_VOC,
                            export_path=train_path,
                            index_file_path=os.path.join(train_path, 'index.tsv'))
