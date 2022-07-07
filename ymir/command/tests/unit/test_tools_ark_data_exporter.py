import logging
import os
import shutil
from typing import List, Tuple
import unittest

from google.protobuf import json_format
import lmdb

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import data_preprocessor, data_reader, data_writer, hash_utils, mir_storage_ops, revs_parser
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
        mir_annotations.ground_truth.CopyFrom(mir_annotations.task_annotations[mir_annotations.head_task_id])

        # keywords
        keywords_dict = {
            'keywords': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'predefined_keyids': [2, 52],
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'predefined_keyids': [52],
                },
            }
        }
        mir_keywords = mirpb.MirKeywords()
        json_format.ParseDict(keywords_dict, mir_keywords)

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

    def __check_lmdb_result(self, asset_ids: List[str], export_path: str, index_file_path: str):
        expected_asset_and_anno_and_gt_keys = {(f"asset_{asset_id}", f"anno_{asset_id}", f"gt_{asset_id}")
                                               for asset_id in asset_ids}
        asset_and_anno_and_gt_keys = set()
        with open(index_file_path, 'r') as f:
            for line in f:
                asset_key, anno_key, gt_key = line.split()
                asset_and_anno_and_gt_keys.add((asset_key, anno_key, gt_key))
        self.assertEqual(expected_asset_and_anno_and_gt_keys, asset_and_anno_and_gt_keys)
        plained_asset_and_anno_and_gtkeys = {k for t in expected_asset_and_anno_and_gt_keys for k in t}
        lmdb_env = lmdb.open(export_path)
        lmdb_tnx = lmdb_env.begin(write=False)

        for k in plained_asset_and_anno_and_gtkeys:
            logging.info(f"plained_asset_and_anno_and_gtkeys: {k}")
            self.assertTrue(lmdb_tnx.get(k.encode()))
        lmdb_env.close()

    # public: test cases
    def test_data_reader_00(self):
        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('tr:a@a', need_tid=True),
                                       asset_ids=set(),
                                       class_ids=set()) as reader:
            self.assertEqual(2, len(list(reader.read())))

        asset_ids = {'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'}
        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=True),
                                       asset_ids=asset_ids,
                                       class_ids=set()) as reader:
            self.assertEqual(2, len(list(reader.read())))

        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('a@a', need_tid=True),
                                       asset_ids=asset_ids,
                                       class_ids={2}) as reader:
            for asset_id, attrs, image_annotations, *_ in reader.read():
                if asset_id == '430df22960b0f369318705800139fcc8ec38a3e4':
                    self.assertEqual(2, len(image_annotations.annotations))
                    self.assertEqual((500, 281), (attrs.width, attrs.height))
            self.assertEqual(2, len(list(reader.read())))

        asset_ids = {'430df22960b0f369318705800139fcc8ec38a3e4'}
        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('tr:a@a', need_tid=True),
                                       asset_ids=asset_ids,
                                       class_ids=set()) as reader:
            self.assertEqual(1, len(list(reader.read())))

    def test_data_rw_00(self):
        train_path = os.path.join(self._dest_root, 'train')

        index_file_path = os.path.join(train_path, 'index.tsv')
        raw_writer = data_writer.RawDataWriter(mir_root=self._mir_root,
                                               assets_location=self._assets_location,
                                               assets_dir=train_path,
                                               annotations_dir=train_path,
                                               need_ext=True,
                                               need_id_sub_folder=False,
                                               overwrite=False,
                                               class_ids_mapping={
                                                   2: 0,
                                                   52: 1
                                               },
                                               format_type=data_writer.AnnoFormat.ANNO_FORMAT_ARK,
                                               index_file_path=index_file_path)
        lmdb_index_file_path = os.path.join(train_path, 'index-lmdb.tsv')
        lmdb_writer = data_writer.LmdbDataWriter(mir_root=self._mir_root,
                                                 assets_location=self._assets_location,
                                                 lmdb_dir=train_path,
                                                 class_ids_mapping={
                                                     2: 0,
                                                     52: 1
                                                 },
                                                 format_type=data_writer.AnnoFormat.ANNO_FORMAT_ARK,
                                                 index_file_path=lmdb_index_file_path)

        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('tr:a@a', need_tid=True),
                                       asset_ids=set(),
                                       class_ids=set()) as reader:
            raw_writer.write_all(reader)
            lmdb_writer.write_all(reader)

        self.__check_result(
            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
            export_path=train_path,
            index_file_path=index_file_path)
        self.__check_lmdb_result(
            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
            export_path=train_path,
            index_file_path=lmdb_index_file_path)

    def test_data_rw_01(self):
        train_path = os.path.join(self._dest_root, 'train')

        index_file_path = os.path.join(train_path, 'index.tsv')

        raw_writer = data_writer.RawDataWriter(mir_root=self._mir_root,
                                               assets_location=self._assets_location,
                                               assets_dir=train_path,
                                               annotations_dir=train_path,
                                               need_ext=True,
                                               need_id_sub_folder=False,
                                               overwrite=False,
                                               class_ids_mapping={
                                                   2: 0,
                                                   52: 1
                                               },
                                               format_type=data_writer.AnnoFormat.ANNO_FORMAT_ARK,
                                               index_file_path=index_file_path,
                                               prep_args={'longside_resize': {
                                                   'dest_size': 250
                                               }})
        lmdb_index_file_path = os.path.join(train_path, 'index-lmdb.tsv')
        lmdb_writer = data_writer.LmdbDataWriter(mir_root=self._mir_root,
                                                 assets_location=self._assets_location,
                                                 lmdb_dir=train_path,
                                                 class_ids_mapping={
                                                     2: 0,
                                                     52: 1
                                                 },
                                                 format_type=data_writer.AnnoFormat.ANNO_FORMAT_ARK,
                                                 index_file_path=lmdb_index_file_path,
                                                 prep_args={'longside_resize': {
                                                     'dest_size': 250
                                                 }})

        with data_reader.MirDataReader(mir_root=self._mir_root,
                                       typ_rev_tid=revs_parser.parse_single_arg_rev('tr:a@a', need_tid=True),
                                       asset_ids=set(),
                                       class_ids=set()) as reader:
            raw_writer.write_all(reader)
            lmdb_writer.write_all(reader)

        self.__check_result(
            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
            export_path=train_path,
            index_file_path=index_file_path)
        self.__check_lmdb_result(
            asset_ids={'430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f'},
            export_path=train_path,
            index_file_path=lmdb_index_file_path)
