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
        dict_asset_cks = dict_annotations.get('image_cks', {})

        task_id = list(dict_annotations['task_annotations'].keys())[0]
        dict_annotations = dict_annotations['task_annotations'][task_id]

        dict_asset_cks_expected = {
            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                'cks': {
                    'weather': 'rainy',
                    'camera': 'camera 1',
                    'theme': 'gray sky'
                },
                'image_quality': 0.83
            },
            '430df22960b0f369318705800139fcc8ec38a3e4': {
                'cks': {
                    'camera': 'camera 0',
                    'theme': 'blue sky',
                    'weather': 'sunny'
                },
                'image_quality': 0.95
            }
        } if with_annotations else {}
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
                            'anno_quality': 0.75,
                            'tags': {
                                'difficult': '0',
                                'pose': 'Unspecified',
                                'color': 'pink'
                            }
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
                            'class_id': 1,
                            'score': 0.5,
                            'anno_quality': 0.62,
                            'tags': {
                                'color': 'white',
                                'pose': 'Frontal',
                                'difficult': '0'
                            }
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
                            'anno_quality': 0.75,
                            'tags': {
                                'difficult': '0',
                                'pose': 'Left',
                                'color': 'blue'
                            }
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
                            'anno_quality': 0.23,
                            'tags': {
                                'difficult': '1',
                                'pose': 'Rear'
                            }
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
                            'anno_quality': 0.35,
                            'tags': {
                                'difficult': '1',
                                'pose': 'Rear'
                            }
                        }]
                    }
                }
            }
        if not with_annotations:
            dict_annotations_expect = {}
        self.assertDictEqual(dict_annotations_expect, dict_annotations)
        self.assertDictEqual(dict_asset_cks_expected, dict_asset_cks)

        # check keywords.mir and contexts.mir
        mir_keywords = mirpb.MirKeywords()
        mir_context = mirpb.MirContext()
        with open(os.path.join(repo_root, 'keywords.mir'), 'rb') as f:
            mir_keywords.ParseFromString(f.read())
        with open(os.path.join(repo_root, 'context.mir'), 'rb') as f:
            mir_context.ParseFromString(f.read())
        dict_keywords = MessageToDict(mir_keywords, preserving_proto_field_name=True)
        dict_context = MessageToDict(mir_context, preserving_proto_field_name=True, including_default_value_fields=True)
        if with_annotations:
            if with_person_ignored:
                dict_keywords_expect = {
                    'keywords': {
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predefined_keyids': [1]
                        },
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predefined_keyids': [1]
                        }
                    },
                    'pred_idx': {
                        'cis': {
                            1: {
                                'key_ids': {
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    },
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    }
                                }
                            }
                        },
                        'tags': {
                            'pose': {
                                'asset_annos': {
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    },
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    }
                                },
                                'sub_indexes': {
                                    'Left': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [1]
                                            }
                                        }
                                    },
                                    'Unspecified': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'Frontal': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0]
                                            }
                                        }
                                    }
                                }
                            },
                            'difficult': {
                                'asset_annos': {
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    },
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    }
                                },
                                'sub_indexes': {
                                    '0': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            },
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0, 1]
                                            }
                                        }
                                    }
                                }
                            },
                            'color': {
                                'asset_annos': {
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    },
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    }
                                },
                                'sub_indexes': {
                                    'blue': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [1]
                                            }
                                        }
                                    },
                                    'pink': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'white': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0]
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'ck_idx': {
                        'theme': {
                            'asset_annos': {
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {},
                                '430df22960b0f369318705800139fcc8ec38a3e4': {}
                            },
                            'sub_indexes': {
                                'blue sky': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
                                    }
                                },
                                'gray sky': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                }
                            }
                        },
                        'weather': {
                            'asset_annos': {
                                '430df22960b0f369318705800139fcc8ec38a3e4': {},
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                            },
                            'sub_indexes': {
                                'sunny': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
                                    }
                                },
                                'rainy': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                }
                            }
                        },
                        'camera': {
                            'asset_annos': {
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {},
                                '430df22960b0f369318705800139fcc8ec38a3e4': {}
                            },
                            'sub_indexes': {
                                'camera 1': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                },
                                'camera 0': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
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
                    'total_asset_mbytes': 1,
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
                    'asset_area_hist': {
                        8000000: 0,
                        6000000: 0,
                        4000000: 0,
                        2000000: 0,
                        1000000: 0,
                        500000: 0,
                        100000: 2,
                        0: 0,
                    },
                    'asset_bytes_hist': {
                        '5.0MB': 0,
                        '4.5MB': 0,
                        '4.0MB': 0,
                        '3.5MB': 0,
                        '3.0MB': 0,
                        '2.5MB': 0,
                        '2.0MB': 0,
                        '1.5MB': 0,
                        '1.0MB': 0,
                        '0.5MB': 0,
                        '0.0MB': 2,
                    },
                    'asset_hw_ratio_hist': {
                        '1.50': 0,
                        '1.40': 0,
                        '1.30': 0,
                        '1.20': 0,
                        '1.10': 0,
                        '1.00': 0,
                        '0.90': 0,
                        '0.80': 0,
                        '0.70': 0,
                        '0.60': 1,
                        '0.50': 1,
                        '0.40': 0,
                        '0.30': 0,
                        '0.20': 0,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'pred_stats': {
                        'total_cnt': 3,
                        'positive_asset_cnt': 2,
                        'negative_asset_cnt': 0,
                        'quality_hist': {
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
                        'area_hist': {
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
                        'area_ratio_hist': {
                            '1.00': 0,
                            '0.90': 0,
                            '0.80': 0,
                            '0.70': 0,
                            '0.60': 0,
                            '0.50': 0,
                            '0.40': 0,
                            '0.30': 0,
                            '0.20': 1,
                            '0.10': 0,
                            '0.00': 2,
                        },
                    },
                }
            else:
                dict_keywords_expect = {
                    'keywords': {
                        '430df22960b0f369318705800139fcc8ec38a3e4': {
                            'predefined_keyids': [1, 2]
                        },
                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                            'predefined_keyids': [1]
                        }
                    },
                    'pred_idx': {
                        'cis': {
                            2: {
                                'key_ids': {
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [2, 3]
                                    }
                                }
                            },
                            1: {
                                'key_ids': {
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    },
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    }
                                }
                            }
                        },
                        'tags': {
                            'color': {
                                'asset_annos': {
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1]
                                    },
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    }
                                },
                                'sub_indexes': {
                                    'pink': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'white': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'blue': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [1]
                                            }
                                        }
                                    }
                                }
                            },
                            'pose': {
                                'asset_annos': {
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1, 2, 3]
                                    },
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    }
                                },
                                'sub_indexes': {
                                    'Frontal': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'Unspecified': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            }
                                        }
                                    },
                                    'Left': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [1]
                                            }
                                        }
                                    },
                                    'Rear': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [2, 3]
                                            }
                                        }
                                    }
                                }
                            },
                            'difficult': {
                                'asset_annos': {
                                    'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                        'ids': [0]
                                    },
                                    '430df22960b0f369318705800139fcc8ec38a3e4': {
                                        'ids': [0, 1, 2, 3]
                                    }
                                },
                                'sub_indexes': {
                                    '1': {
                                        'key_ids': {
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [2, 3]
                                            }
                                        }
                                    },
                                    '0': {
                                        'key_ids': {
                                            'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                                                'ids': [0]
                                            },
                                            '430df22960b0f369318705800139fcc8ec38a3e4': {
                                                'ids': [0, 1]
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'ck_idx': {
                        'camera': {
                            'asset_annos': {
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {},
                                '430df22960b0f369318705800139fcc8ec38a3e4': {}
                            },
                            'sub_indexes': {
                                'camera 1': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                },
                                'camera 0': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
                                    }
                                }
                            }
                        },
                        'weather': {
                            'asset_annos': {
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {},
                                '430df22960b0f369318705800139fcc8ec38a3e4': {}
                            },
                            'sub_indexes': {
                                'rainy': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                },
                                'sunny': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
                                    }
                                }
                            }
                        },
                        'theme': {
                            'asset_annos': {
                                '430df22960b0f369318705800139fcc8ec38a3e4': {},
                                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                            },
                            'sub_indexes': {
                                'gray sky': {
                                    'key_ids': {
                                        'a3008c032eb11c8d9ffcb58208a36682ee40900f': {}
                                    }
                                },
                                'blue sky': {
                                    'key_ids': {
                                        '430df22960b0f369318705800139fcc8ec38a3e4': {}
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
                    'total_asset_mbytes': 1,
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
                    'asset_area_hist': {
                        8000000: 0,
                        6000000: 0,
                        4000000: 0,
                        2000000: 0,
                        1000000: 0,
                        500000: 0,
                        100000: 2,
                        0: 0,
                    },
                    'asset_bytes_hist': {
                        '5.0MB': 0,
                        '4.5MB': 0,
                        '4.0MB': 0,
                        '3.5MB': 0,
                        '3.0MB': 0,
                        '2.5MB': 0,
                        '2.0MB': 0,
                        '1.5MB': 0,
                        '1.0MB': 0,
                        '0.5MB': 0,
                        '0.0MB': 2,
                    },
                    'asset_hw_ratio_hist': {
                        '1.50': 0,
                        '1.40': 0,
                        '1.30': 0,
                        '1.20': 0,
                        '1.10': 0,
                        '1.00': 0,
                        '0.90': 0,
                        '0.80': 0,
                        '0.70': 0,
                        '0.60': 1,
                        '0.50': 1,
                        '0.40': 0,
                        '0.30': 0,
                        '0.20': 0,
                        '0.10': 0,
                        '0.00': 0,
                    },
                    'pred_stats': {
                        'total_cnt': 5,
                        'positive_asset_cnt': 2,
                        'negative_asset_cnt': 0,
                        'quality_hist': {
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
                        'area_hist': {
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
                        'area_ratio_hist': {
                            '1.00': 0,
                            '0.90': 0,
                            '0.80': 0,
                            '0.70': 0,
                            '0.60': 0,
                            '0.50': 0,
                            '0.40': 0,
                            '0.30': 0,
                            '0.20': 1,
                            '0.10': 0,
                            '0.00': 4,
                        },
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
