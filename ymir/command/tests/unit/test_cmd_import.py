import logging
import os
import shutil
import unittest

from google.protobuf.json_format import MessageToDict

from mir.commands.importing import CmdImport
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdImport(unittest.TestCase):
    _USER_NAME = 'test_user'
    _MIR_REPO_NAME = 'mir-test-repo'
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
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['cat', 'airplane,aeroplane', 'person'])
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
        args.dst_rev = 'a@import-task-0'
        args.index_file = self._idx_file
        args.ck_file = self._ck_file
        args.anno = self._data_xml_path
        args.gen = gen_folder
        args.dataset_name = ''
        args.work_dir = self._work_dir
        args.ignore_unknown_types = False
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=True)

        # not write person label
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['cat', 'airplane,aeroplane'])

        # ignore unknown types
        args.ignore_unknown_types = True
        args.dataset_name = 'import-task-0'
        args.dst_rev = 'a@import-task-1'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=True, with_annotations=True)

        # have no annotations
        args.anno = None
        args.ignore_unknown_types = False
        args.dataset_name = 'import-task-0'
        args.dst_rev = 'a@import-task-2'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret == MirCode.RC_OK
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=False)

        # check for relative path, currently should return an error code
        args.mir_root = 'abc'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        assert ret != MirCode.RC_OK

        args.index_file = ''
        assert CmdImport(args).run() != MirCode.RC_OK
        args.index_file = self._idx_file

        args.anno = ''
        assert CmdImport(args).run() != MirCode.RC_OK
        args.anno = self._data_xml_path + '/fake-one'
        assert CmdImport(args).run() != MirCode.RC_OK
        args.anno = self._data_xml_path

    def _check_repo(self, repo_root: str, with_person_ignored: bool, with_annotations: bool):
        # check annotations.mir
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
                            'class_id': 1,
                            'score': 2.0,
                            'tags': {
                                'difficult': '0',
                                'color': 'pink',
                                'pose': 'Unspecified'
                            },
                            'anno_quality': 0.75,
                        }],
                        'cks': {
                            'weather': 'rainy',
                            'camera': 'camera 1',
                            'theme': 'gray sky'
                        },
                        'image_quality':
                        0.83,
                    },
                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                        'annotations': [{
                            'box': {
                                'x': 104,
                                'y': 78,
                                'w': 272,
                                'h': 106
                            },
                            'class_id': 1,
                            'score': 0.5,
                            'tags': {
                                'difficult': '0',
                                'color': 'white',
                                'pose': 'Frontal'
                            },
                            'anno_quality': 0.62,
                        }, {
                            'index': 1,
                            'box': {
                                'x': 133,
                                'y': 88,
                                'w': 65,
                                'h': 36
                            },
                            'class_id': 1,
                            'score': 2.0,
                            'tags': {
                                'difficult': '0',
                                'color': 'blue',
                                'pose': 'Left'
                            },
                            'anno_quality': 0.75,
                        }],
                        'cks': {
                            'weather': 'sunny',
                            'camera': 'camera 0',
                            'theme': 'blue sky'
                        },
                        'image_quality':
                        0.95,
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
                            'class_id': 1,
                            'score': 2.0,
                            'tags': {
                                'difficult': '0',
                                'color': 'pink',
                                'pose': 'Unspecified'
                            },
                            'anno_quality': 0.75,
                        }],
                        'cks': {
                            'weather': 'rainy',
                            'camera': 'camera 1',
                            'theme': 'gray sky'
                        },
                        'image_quality':
                        0.83,
                    },
                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                        'annotations': [{
                            'box': {
                                'x': 104,
                                'y': 78,
                                'w': 272,
                                'h': 106
                            },
                            'class_id': 1,
                            'score': 0.5,
                            'tags': {
                                'difficult': '0',
                                'color': 'white',
                                'pose': 'Frontal'
                            },
                            'anno_quality': 0.62,
                        }, {
                            'index': 1,
                            'box': {
                                'x': 133,
                                'y': 88,
                                'w': 65,
                                'h': 36
                            },
                            'class_id': 1,
                            'score': 2.0,
                            'tags': {
                                'difficult': '0',
                                'color': 'blue',
                                'pose': 'Left'
                            },
                            'anno_quality': 0.75,
                        }, {
                            'index': 2,
                            'box': {
                                'x': 195,
                                'y': 180,
                                'w': 19,
                                'h': 50
                            },
                            'class_id': 2,
                            'score': 2.0,
                            'tags': {
                                'difficult': '1',
                                'pose': 'Rear'
                            },
                            'anno_quality': 0.23,
                        }, {
                            'index': 3,
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'class_id': 2,
                            'score': 2.0,
                            'tags': {
                                'difficult': '1',
                                'pose': 'Rear'
                            },
                            'anno_quality': 0.35,
                        }],
                        'cks': {
                            'weather': 'sunny',
                            'camera': 'camera 0',
                            'theme': 'blue sky'
                        },
                        'image_quality':
                        0.95,
                    }
                }
            }
        if not with_annotations:
            dict_annotations_expect = {}
        self.assertDictEqual(dict_annotations_expect, dict_annotations)

        # check keywords.mir and contexts.mir
        mir_keywords = mirpb.MirKeywords()
        mir_context = mirpb.MirContext()
        with open(os.path.join(repo_root, 'keywords.mir'), 'rb') as f:
            mir_keywords.ParseFromString(f.read())
            # sort asset-anno pairs before compare, they don't have orders when save
            for _, ci_to_assets in mir_keywords.pred_idx.asset_cis.items():
                ci_to_assets.indexes.sort(key=lambda x: (x.asset_id, x.anno_idx))
            for _, ci_to_annos in mir_keywords.pred_idx.anno_cis.items():
                ci_to_annos.indexes.sort(key=lambda x: (x.asset_id, x.anno_idx))
            for _, ck_to_assets in mir_keywords.pred_idx.asset_cks.items():
                ck_to_assets.indexes.sort(key=lambda x: (x.asset_id, x.anno_idx))
                for _, sub_ck_to_assets in ck_to_assets.sub_indexes.items():
                    sub_ck_to_assets.pairs.sort(key=lambda x: (x.asset_id, x.anno_idx))
            for _, ck_to_annos in mir_keywords.pred_idx.anno_cks.items():
                ck_to_annos.indexes.sort(key=lambda x: (x.asset_id, x.anno_idx))
                for _, sub_ck_to_annos in ck_to_annos.sub_indexes.items():
                    sub_ck_to_annos.pairs.sort(key=lambda x: (x.asset_id, x.anno_idx))
        with open(os.path.join(repo_root, 'context.mir'), 'rb') as f:
            mir_context.ParseFromString(f.read())
        dict_keywords = MessageToDict(mir_keywords, preserving_proto_field_name=True)
        dict_context = MessageToDict(mir_context, preserving_proto_field_name=True, including_default_value_fields=True)
        if with_annotations:
            if with_person_ignored:
                dict_keywords_expect = {
                    'keywords': {
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predefined_keyids': [1]
                        },
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predefined_keyids': [1]
                        }
                    },
                    'pred_idx': {
                        'asset_cis': {
                            1: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }]
                            }
                        },
                        'asset_cks': {
                            'theme': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'blue sky': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'gray sky': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            },
                            'camera': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'camera 0': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'camera 1': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            },
                            'weather': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'rainy': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'sunny': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            }
                        },
                        'anno_cis': {
                            1: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }]
                            }
                        },
                        'anno_cks': {
                            'color': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    'white': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }]
                                    },
                                    'pink': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    },
                                    'blue': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }]
                                    }
                                }
                            },
                            'difficult': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    '0': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }, {
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }, {
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    }
                                }
                            },
                            'pose': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    'Left': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }]
                                    },
                                    'Frontal': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }]
                                    },
                                    'Unspecified': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    }
                                }
                            }
                        }
                    }
                }
                dict_context_expected = {
                    'images_cnt': 2,
                    'predefined_keyids_cnt': {
                        1: 2
                    },
                    'negative_images_cnt': 0,
                    'project_negative_images_cnt': 0,
                    'project_predefined_keyids_cnt': {},
                    'cks_cnt': {
                        'weather': {
                            'cnt': 2,
                            'sub_cnt': {
                                'sunny': 1,
                                'rainy': 1,
                            },
                        },
                        'camera': {
                            'cnt': 2,
                            'sub_cnt': {
                                'camera 0': 1,
                                'camera 1': 1,
                            },
                        },
                        'theme': {
                            'cnt': 2,
                            'sub_cnt': {
                                'blue sky': 1,
                                'gray sky': 1,
                            },
                        }
                    },
                    'tags_cnt': {
                        'difficult': {
                            'cnt': 3,
                            'sub_cnt': {
                                '0': 3,
                            },
                        },
                        'color': {
                            'cnt': 3,
                            'sub_cnt': {
                                'white': 1,
                                'blue': 1,
                                'pink': 1,
                            },
                        },
                        'pose': {
                            'cnt': 3,
                            'sub_cnt': {
                                'Left': 1,
                                'Frontal': 1,
                                'Unspecified': 1,
                            },
                        },
                    },
                    'asset_quality_hist': {
                        '1.00': 0,
                        '0.90': 1,
                        '0.80': 1,
                        '0.70': 0,
                        '0.60': 0,
                        '0.50': 0,
                        '0.40': 0,
                        '0.30': 0,
                        '0.20': 0,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'anno_quality_hist': {
                        '1.00': 0,
                        '0.90': 0,
                        '0.80': 0,
                        '0.70': 2,
                        '0.60': 1,
                        '0.50': 0,
                        '0.40': 0,
                        '0.30': 0,
                        '0.20': 0,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'anno_area_hist': {
                        200000: 0,
                        100000: 0,
                        50000: 0,
                        10000: 1,
                        5000: 1,
                        2500: 0,
                        500: 1,
                        50: 0,
                        0: 0,
                    },
                }
            else:
                dict_keywords_expect = {
                    'keywords': {
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predefined_keyids': [1]
                        },
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predefined_keyids': [1, 2]
                        }
                    },
                    'pred_idx': {
                        'asset_cis': {
                            1: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }]
                            },
                            2: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }]
                            }
                        },
                        'asset_cks': {
                            'camera': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'camera 1': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'camera 0': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            },
                            'theme': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'gray sky': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'blue sky': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            },
                            'weather': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': -1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                    'anno_idx': -1
                                }],
                                'sub_indexes': {
                                    'rainy': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f',
                                            'anno_idx': -1
                                        }]
                                    },
                                    'sunny': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': -1
                                        }]
                                    }
                                }
                            }
                        },
                        'anno_cis': {
                            2: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 2
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 3
                                }]
                            },
                            1: {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }]
                            }
                        },
                        'anno_cks': {
                            'color': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    'pink': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    },
                                    'white': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }]
                                    },
                                    'blue': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }]
                                    }
                                }
                            },
                            'difficult': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 2
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 3
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    '0': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }, {
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }, {
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    },
                                    '1': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 2
                                        }, {
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 3
                                        }]
                                    }
                                }
                            },
                            'pose': {
                                'indexes': [{
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 1
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 2
                                }, {
                                    'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                    'anno_idx': 3
                                }, {
                                    'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                }],
                                'sub_indexes': {
                                    'Rear': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 2
                                        }, {
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 3
                                        }]
                                    },
                                    'Frontal': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4'
                                        }]
                                    },
                                    'Unspecified': {
                                        'pairs': [{
                                            'asset_id': 'a3008c032eb11c8d9ffcb58208a36682ee40900f'
                                        }]
                                    },
                                    'Left': {
                                        'pairs': [{
                                            'asset_id': '430df22960b0f369318705800139fcc8ec38a3e4',
                                            'anno_idx': 1
                                        }]
                                    }
                                }
                            }
                        }
                    }
                }
                dict_context_expected = {
                    'images_cnt': 2,
                    'predefined_keyids_cnt': {
                        1: 2,
                        2: 1
                    },
                    'negative_images_cnt': 0,
                    'project_negative_images_cnt': 0,
                    'project_predefined_keyids_cnt': {},
                    'cks_cnt': {
                        'weather': {
                            'cnt': 2,
                            'sub_cnt': {
                                'sunny': 1,
                                'rainy': 1,
                            },
                        },
                        'camera': {
                            'cnt': 2,
                            'sub_cnt': {
                                'camera 0': 1,
                                'camera 1': 1,
                            },
                        },
                        'theme': {
                            'cnt': 2,
                            'sub_cnt': {
                                'blue sky': 1,
                                'gray sky': 1,
                            },
                        }
                    },
                    'tags_cnt': {
                        'difficult': {
                            'cnt': 5,
                            'sub_cnt': {
                                '0': 3,
                                '1': 2,
                            },
                        },
                        'color': {
                            'cnt': 3,
                            'sub_cnt': {
                                'white': 1,
                                'blue': 1,
                                'pink': 1,
                            },
                        },
                        'pose': {
                            'cnt': 5,
                            'sub_cnt': {
                                'Left': 1,
                                'Frontal': 1,
                                'Unspecified': 1,
                                'Rear': 2,
                            },
                        },
                    },
                    'asset_quality_hist': {
                        '1.00': 0,
                        '0.90': 1,
                        '0.80': 1,
                        '0.70': 0,
                        '0.60': 0,
                        '0.50': 0,
                        '0.40': 0,
                        '0.30': 0,
                        '0.20': 0,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'anno_quality_hist': {
                        '1.00': 0,
                        '0.90': 0,
                        '0.80': 0,
                        '0.70': 2,
                        '0.60': 1,
                        '0.50': 0,
                        '0.40': 0,
                        '0.30': 1,
                        '0.20': 1,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'anno_area_hist': {
                        200000: 0,
                        100000: 0,
                        50000: 0,
                        10000: 1,
                        5000: 1,
                        2500: 0,
                        500: 3,
                        50: 0,
                        0: 0,
                    },
                }
            try:
                self.assertDictEqual(dict_keywords, dict_keywords_expect)
            except AssertionError as e:
                logging.info(f"expected: {dict_keywords_expect}")
                logging.info(f"actual: {dict_keywords}")
                raise e
            try:
                self.assertDictEqual(dict_context, dict_context_expected)
            except AssertionError as e:
                logging.info(f"expected: {dict_context_expected}")
                logging.info(f"actual: {dict_context}")
                raise e
        else:
            self.assertEqual(0, len(dict_keywords))
            self.assertEqual(0, len(dict_context['predefined_keyids_cnt']))

        # check metadatas.mir
        mir_metadatas = mirpb.MirMetadatas()
        with open(os.path.join(repo_root, 'metadatas.mir'), 'rb') as f:
            mir_metadatas.ParseFromString(f.read())
        dict_metadatas = MessageToDict(mir_metadatas, preserving_proto_field_name=True)
        dict_metadatas_expect = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'dataset_name': 'import-task-0',
                    'asset_type': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 281,
                    'image_channels': 3
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'dataset_name': 'import-task-0',
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

        # check tasks.mir
        mir_tasks = mirpb.MirTasks()
        with open(os.path.join(repo_root, 'tasks.mir'), 'rb') as f:
            mir_tasks.ParseFromString(f.read())
        dict_tasks = MessageToDict(mir_tasks, preserving_proto_field_name=True)
        assert ('import-task-0' in dict_tasks['tasks'] or 'import-task-1' in dict_tasks['tasks']
                or 'import-task-2' in dict_tasks['tasks'])

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


if __name__ == '__main__':
    unittest.main()
