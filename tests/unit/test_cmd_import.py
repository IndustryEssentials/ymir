import logging
import os
import shutil
from typing import List
import unittest

from google.protobuf.json_format import MessageToDict

from mir.commands.importing import CmdImport
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdImport(unittest.TestCase):
    _USER_NAME = 'test_user'
    _MIR_REPO_NAME = 'ymir-dvc-test'
    _STORAGE_NAME = 'monitor_storage_root'

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._sandbox_root = test_utils.dir_test_root(self.id().split('.')[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._USER_NAME)
        self._mir_repo_root = os.path.join(self._user_root, self._MIR_REPO_NAME)
        self._storage_root = os.path.join(self._sandbox_root, self._STORAGE_NAME)
        self._work_dir = os.path.join(self._sandbox_root, 'work_dir')
        self.maxDiff = None

    def setUp(self) -> None:
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_labels_csv(['cat', 'airplane,aeroplane', 'person'])
        self._prepare_mir_repo()

        self._cur_path = os.getcwd()
        os.chdir(self._mir_repo_root)

    def tearDown(self) -> None:
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.chdir(self._cur_path)

    def test_import_cmd_00(self):
        # normal
        mir_root = self._mir_repo_root
        gen_folder = os.path.join(self._storage_root, 'gen')
        args = type('', (), {})()
        args.mir_root = mir_root
        args.src_revs = ''
        args.dst_rev = 'a@import-task-id'
        args.index_file = self._idx_file
        args.ck_file = self._ck_file
        args.anno = self._data_xml_path
        args.gen = gen_folder
        args.dataset_name = 'import-task-branch'
        args.work_dir = self._work_dir
        args.ignore_unknown_types = False
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=True)

        # not write person label
        self._prepare_labels_csv(['cat', 'airplane,aeroplane'])

        # ignore unknown types
        args.ignore_unknown_types = True
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=True, with_annotations=True)

        # have no annotations
        args.anno = None
        args.ignore_unknown_types = False
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=False)

        # check for relative path, currently should return an error code
        args.mir_root = 'abc'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret != MirCode.RC_OK

    def _check_repo(self, repo_root: str, with_person_ignored: bool, with_annotations: bool):
        mir_annotations = mirpb.MirAnnotations()
        with open(os.path.join(repo_root, 'annotations.mir'), 'rb') as f:
            mir_annotations.ParseFromString(f.read())
        dict_annotations = MessageToDict(mir_annotations, preserving_proto_field_name=True)
        task_id = list(dict_annotations['task_annotations'].keys())[0]
        dict_annotations = dict_annotations['task_annotations'][task_id]
        if with_person_ignored:
            dict_annotations_expect = {
                'image_annotations': {
                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                        'annotations': [{
                            'box': {
                                'x': 181,
                                'y': 127,
                                'w': 94,
                                'h': 67
                            },
                            'class_id': 1
                        }]
                    },
                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                        'annotations': [{
                            'box': {
                                'x': 104,
                                'y': 78,
                                'w': 272,
                                'h': 106
                            },
                            'class_id': 1
                        }, {
                            'index': 1,
                            'box': {
                                'x': 133,
                                'y': 88,
                                'w': 65,
                                'h': 36
                            },
                            'class_id': 1
                        }]
                    }
                }
            }
        else:
            dict_annotations_expect = {
                'image_annotations': {
                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                        'annotations': [{
                            'box': {
                                'x': 181,
                                'y': 127,
                                'w': 94,
                                'h': 67
                            },
                            'class_id': 1
                        }]
                    },
                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                        'annotations': [{
                            'box': {
                                'x': 104,
                                'y': 78,
                                'w': 272,
                                'h': 106
                            },
                            'class_id': 1
                        }, {
                            'index': 1,
                            'box': {
                                'x': 133,
                                'y': 88,
                                'w': 65,
                                'h': 36
                            },
                            'class_id': 1
                        }, {
                            'index': 2,
                            'box': {
                                'x': 195,
                                'y': 180,
                                'w': 19,
                                'h': 50
                            },
                            'class_id': 2
                        }, {
                            'index': 3,
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'class_id': 2
                        }]
                    }
                }
            }
        if not with_annotations:
            dict_annotations_expect = {}
        self.assertDictEqual(dict_annotations_expect, dict_annotations)

        mir_keywords = mirpb.MirKeywords()
        with open(os.path.join(repo_root, 'keywords.mir'), 'rb') as f:
            mir_keywords.ParseFromString(f.read())
        dict_keywords = MessageToDict(mir_keywords, preserving_proto_field_name=True)
        if with_annotations:
            dup_asset_id = '430df22960b0f369318705800139fcc8ec38a3e4'
            dict_keywords['keywords'][dup_asset_id]['predifined_keyids'] = sorted(
                dict_keywords['keywords'][dup_asset_id]['predifined_keyids'])  # Protobuf does not care about order of list.
            dup_keywords_id = 1
            dict_keywords['index_predifined_keyids'][dup_keywords_id]['asset_ids'] = sorted(
                dict_keywords['index_predifined_keyids'][dup_keywords_id]['asset_ids'])
            if with_person_ignored:
                dict_keywords_expect = {
                    'keywords': {
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predifined_keyids': [1],
                        },
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predifined_keyids': [1],
                        }
                    },
                    'predifined_keyids_cnt': {
                        1: 2
                    },
                    'predifined_keyids_total': 2,
                    'index_predifined_keyids': {
                        1: {
                            'asset_ids':
                            ['430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f']
                        }
                    },
                }
            else:
                dict_keywords_expect = {
                    'keywords': {
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predifined_keyids': [1],
                        },
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predifined_keyids': [1, 2],
                        }
                    },
                    'predifined_keyids_cnt': {
                        1: 2,
                        2: 1
                    },
                    'predifined_keyids_total': 3,
                    'index_predifined_keyids': {
                        2: {
                            'asset_ids': ['430df22960b0f369318705800139fcc8ec38a3e4']
                        },
                        1: {
                            'asset_ids':
                            ['430df22960b0f369318705800139fcc8ec38a3e4', 'a3008c032eb11c8d9ffcb58208a36682ee40900f']
                        }
                    },
                }
            try:
                self.assertDictEqual(dict_keywords, dict_keywords_expect)
            except AssertionError as e:
                logging.info(f"expected: {dict_keywords_expect}")
                logging.info(f"actual: {dict_keywords}")
                raise e
        else:
            self.assertEqual(0, len(dict_keywords))

        mir_metadatas = mirpb.MirMetadatas()
        with open(os.path.join(repo_root, 'metadatas.mir'), 'rb') as f:
            mir_metadatas.ParseFromString(f.read())
        dict_metadatas = MessageToDict(mir_metadatas, preserving_proto_field_name=True)
        dict_metadatas_expect = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'dataset_name': 'import-task-branch',
                    'asset_type': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 281,
                    'image_channels': 3
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'dataset_name': 'import-task-branch',
                    'asset_type': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 333,
                    'image_channels': 3
                }
            }
        }
        for key in list(dict_metadatas['attributes'].keys()):
            actual = dict_metadatas['attributes'][key]
            expected = dict_metadatas_expect['attributes'][key]
            for sub_key, expected_value in expected.items():
                self.assertEqual(actual[sub_key], expected_value)

        mir_tasks = mirpb.MirTasks()
        with open(os.path.join(repo_root, 'tasks.mir'), 'rb') as f:
            mir_tasks.ParseFromString(f.read())
        dict_tasks = MessageToDict(mir_tasks, preserving_proto_field_name=True)
        assert 'import-task-id' in dict_tasks['tasks']

    # custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            logging.info('sandbox root exists, remove it first')
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

        self._data_root = os.path.join(self._storage_root, 'data')
        os.makedirs(self._data_root)

        self._idx_file = os.path.join(self._data_root, 'idx.txt')
        self._ck_file = os.path.join(self._data_root, 'ck.tsv')
        self._data_img_path = os.path.join(self._data_root, 'img')
        os.makedirs(self._data_img_path)
        self._data_xml_path = os.path.join(self._data_root, 'xml')
        os.makedirs(self._data_xml_path)

        self._prepare_data(data_root=self._data_root,
                           idx_file=self._idx_file,
                           ck_file=self._ck_file,
                           data_img_path=self._data_img_path,
                           data_xml_path=self._data_xml_path)

    def _prepare_data(self, data_root, idx_file, ck_file, data_img_path, data_xml_path):
        local_data_root = 'tests/assets'

        # Copy img files.
        img_files = ['2007_000032.jpg', '2007_000243.jpg']
        with open(idx_file, 'w') as idx_f, open(ck_file, 'w') as ck_f:
            for file in img_files:
                src = os.path.join(local_data_root, file)
                dst = os.path.join(data_img_path, file)
                shutil.copyfile(src, dst)

                idx_f.writelines(dst + '\n')
                ck_f.write(f"{dst}\tck0\n")

        # Copy xml files.
        xml_files = ['2007_000032.xml', '2007_000243.xml']
        for file in xml_files:
            src = os.path.join(local_data_root, file)
            dst = os.path.join(data_xml_path, file)
            shutil.copyfile(src, dst)

    def _prepare_mir_repo(self):
        # init repo
        test_utils.mir_repo_init(self._mir_repo_root)
        # prepare branch a
        test_utils.mir_repo_create_branch(self._mir_repo_root, 'a')

    def _prepare_labels_csv(self, names: List[str]):
        with open(class_ids.ids_file_path(mir_root=self._mir_repo_root), 'w') as f:
            f.write('# some comments')
            for index, name in enumerate(names):
                f.write(f"{index},,{name}\n")


if __name__ == '__main__':
    unittest.main()
