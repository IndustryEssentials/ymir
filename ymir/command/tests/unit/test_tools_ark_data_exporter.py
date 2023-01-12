import os
import shutil
from typing import List, Tuple
import unittest

from google.protobuf import json_format

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import exporter, mir_storage_ops, revs_parser, mir_storage
from mir.tools.mir_storage import sha1sum_for_file
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
        sha1sum_path_pairs = [(sha1sum_for_file(image_path), image_path)
                              for image_path in image_paths]  # type: List[Tuple[str, str]]
        for sha1sum, image_path in sha1sum_path_pairs:
            shutil.copyfile(image_path,
                            mir_storage.get_asset_storage_path(self._assets_location, sha1sum))

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
                    'imageChannels': 3,
                    'tvtType': 'TvtTypeTraining',
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 333,
                    'imageChannels': 3,
                }
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        # annotations
        annotations_dict = {
            'prediction': {
                'task_id': 'a',
                'type': mirpb.ObjectType.OT_NO_ANNOTATIONS,
                'image_annotations': {
                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                        'boxes': [{
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
                        'boxes': [{
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
            },
            'ground_truth': {
                'type': mirpb.ObjectType.OT_NO_ANNOTATIONS,
            }
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)
        mir_annotations.ground_truth.CopyFrom(mir_annotations.prediction)

        # task
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='a', message='import')

        # save and commit
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    # private: check result
    def __check_result(self, asset_ids: List[str], export_path: str, index_file_path: str):
        #   index file exists
        self.assertTrue(os.path.isfile(index_file_path))
        #   index file have enough lines
        #   and each line is accessable
        with open(index_file_path, 'r') as idx_f:
            lines = idx_f.readlines()
            self.assertEqual(len(lines), len(asset_ids))
            for line in lines:
                asset_rel_path, annotation_rel_path = line.split()
                self.assertTrue(os.path.isfile(os.path.join(export_path, asset_rel_path)))
                self.assertTrue(os.path.isfile(os.path.join(export_path, annotation_rel_path)))

    def __check_ark_annotations(self, asset_id: str, export_path: str, expected_first_two_cols: List[Tuple[int, int]]):
        annotation_path = os.path.join(export_path, asset_id + '.txt')
        with open(annotation_path, 'r') as f:
            lines = f.read().splitlines()
        self.assertEqual(len(expected_first_two_cols), len(lines))
        for line_idx, line in enumerate(lines):
            line_components = line.split(',')
            for col_idx in range(2):
                self.assertEqual(expected_first_two_cols[line_idx][col_idx], int(line_components[col_idx].strip()))

    def test_data_rw_00(self):
        train_path = os.path.join(self._dest_root, 'train')

        index_file_path = os.path.join(train_path, 'index.tsv')

        mir_metadatas: mirpb.MirMetadatas
        mir_annotations: mirpb.MirAnnotations
        typ_rev_tid = revs_parser.parse_single_arg_rev('tr:a@a', need_tid=True)
        [mir_metadatas, mir_annotations] = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch=typ_rev_tid.rev,
            mir_task_id=typ_rev_tid.tid,
            ms_list=[mirpb.MirStorage.MIR_METADATAS, mirpb.MirStorage.MIR_ANNOTATIONS],
        )
        ec = mirpb.ExportConfig(asset_format=mirpb.AssetFormat.AF_RAW,
                                asset_dir=train_path,
                                media_location=self._assets_location,
                                need_sub_folder=False,
                                anno_format=mirpb.ExportFormat.EF_ARK_TXT,
                                gt_dir=train_path,)
        exporter.export_mirdatas_to_dir(
            mir_metadatas=mir_metadatas,
            ec=ec,
            mir_annotations=mir_annotations,
            class_ids_mapping={2: 0, 52: 1},
            cls_id_mgr=None,
        )

        self.__check_result(
            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
            export_path=train_path,
            index_file_path=index_file_path)
