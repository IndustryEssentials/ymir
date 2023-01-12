import os
import shutil
from typing import List, Tuple
import unittest

from google.protobuf import json_format

from mir.commands import export
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops, mir_storage
from mir.tools.class_ids import ids_file_path
from mir.tools.code import MirCode
from mir.tools.mir_storage import sha1sum_for_file
from tests import utils as test_utils


class TestCmdExport(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._assets_location = os.path.join(self._test_root, 'assets_location')
        self._dest_root = os.path.join(self._test_root, 'export_dest')
        self._gt_root = os.path.join(self._dest_root, 'gt_dir')
        self._mir_root = os.path.join(self._test_root, 'mir-repo')

    def setUp(self) -> None:
        self.__prepare_dirs()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['freshbee', 'type1', 'person', 'airplane,aeroplane'])
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
            'prediction': {
                'task_id': 'a',
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
                            'class_id': 3,
                            'score': 1,
                            'anno_quality': 0.95,
                            'tags': {
                                'fake tag name': 'fake tag data'
                            },
                        }, {
                            'index': 1,
                            'box': {
                                'x': 133,
                                'y': 88,
                                'w': 65,
                                'h': 36
                            },
                            'class_id': 3,
                            'score': 1,
                            'anno_quality': 0.95,
                            'tags': {
                                'fake tag name': 'fake tag data'
                            },
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
                            'anno_quality': 0.95,
                            'tags': {
                                'fake tag name': 'fake tag data'
                            },
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
                            'anno_quality': 0.95,
                            'tags': {
                                'fake tag name': 'fake tag data'
                            },
                        }],
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
                            'class_id': 3,
                            'score': 1,
                            'anno_quality': 0.95,
                            'tags': {
                                'fake tag name': 'fake tag data'
                            },
                        }],
                    },
                },
                'type': mirpb.ObjectType.OT_DET_BOX,
            },
            'ground_truth': {
                'type': mirpb.ObjectType.OT_NO_ANNOTATIONS,
            },
            'image_cks': {
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'cks': {
                        'weather': 'sunny',
                    },
                    'image_quality': 0.5
                },
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'cks': {
                        'weather': 'sunny',
                    },
                    'image_quality': 0.3
                }
            }
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        # tasks
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData,
                                           task_id='a',
                                           message='test_tools_data_exporter_branch_a')

        # save and commit
        mir_datas = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas=mir_datas,
                                                      task=task)

    def test_normal_00(self):
        # normal case: voc:raw
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.label_storage_file = ids_file_path(self._mir_root)
        fake_args.asset_dir = self._dest_root
        fake_args.pred_dir = self._dest_root
        fake_args.gt_dir = self._gt_root
        fake_args.media_location = self._assets_location
        fake_args.src_revs = 'a@a'
        fake_args.anno_format = 'voc'
        fake_args.asset_format = 'raw'
        fake_args.class_names = 'person'
        fake_args.work_dir = ''
        runner = export.CmdExport(fake_args)
        result = runner.run()
        self.assertEqual(MirCode.RC_OK, result)

        # abnormal case: no asset_dir, pred_dir, media_location
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.label_storage_file = ids_file_path(self._mir_root)
        fake_args.asset_dir = ''
        fake_args.pred_dir = ''
        fake_args.gt_dir = ''
        fake_args.media_location = ''
        fake_args.src_revs = 'a@a'
        fake_args.anno_format = 'voc'
        fake_args.asset_format = 'raw'
        fake_args.class_names = 'person'
        fake_args.work_dir = ''
        runner = export.CmdExport(fake_args)
        result = runner.run()
        self.assertNotEqual(MirCode.RC_OK, result)
