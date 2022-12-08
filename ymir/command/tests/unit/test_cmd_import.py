import logging
import os
import shutil
from typing import Set
import unittest

from google.protobuf.json_format import MessageToDict, ParseDict

from mir.commands.import_dataset import CmdImport
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.class_ids import ids_file_path
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdImport(unittest.TestCase):
    _USER_NAME = 'test_user'
    _MIR_REPO_NAME = 'mir-test-repo'
    _STORAGE_NAME = 'monitor_storage_root'

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.maxDiff = None
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
        args.label_storage_file = ids_file_path(mir_root)
        args.src_revs = ''
        args.dst_rev = 'a@import-task-0'
        args.index_file = self._idx_file
        args.ck_file = self._ck_file
        args.pred_dir = self._data_xml_path
        args.gt_dir = self._data_xml_path
        args.gen_abs = gen_folder
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'stop'
        args.anno_type = 'det-box'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=True)

        # not write person label
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['cat', 'airplane,aeroplane'])

        # ignore unknown types
        args.unknown_types_strategy = 'ignore'
        args.dst_rev = 'a@import-task-1'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo(self._mir_repo_root,
                         with_person_ignored=True,
                         with_annotations=True,
                         task_new_types={'person': 3},
                         task_new_types_added=False)

        # add unknown types
        args.unknown_types_strategy = 'add'
        args.dst_rev = 'a@import-task-2'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo(self._mir_repo_root,
                         with_person_ignored=False,
                         with_annotations=True,
                         task_new_types={'person': 3},
                         task_new_types_added=True)

        # have no annotations
        args.pred_dir = None
        args.gt_dir = None
        args.unknown_types_strategy = 'stop'
        args.dst_rev = 'a@import-task-3'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo(self._mir_repo_root, with_person_ignored=False, with_annotations=False)

        # check for relative path, currently should return an error code
        args.mir_root = 'abc'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertNotEqual(ret, MirCode.RC_OK)
        args.mir_root = self._mir_repo_root

        args.index_file = ''
        self.assertNotEqual(CmdImport(args).run(), MirCode.RC_OK)
        args.index_file = self._idx_file

        args.pred_dir = ''
        self.assertEqual(CmdImport(args).run(), MirCode.RC_OK)
        args.pred_dir = self._data_xml_path + '/fake-one'
        self.assertNotEqual(CmdImport(args).run(), MirCode.RC_OK)
        args.pred_dir = self._data_xml_path

    def test_import_cmd_01(self):
        shutil.move(os.path.join(self._data_xml_path, 'pred_meta.yaml'), os.path.join(self._data_xml_path, 'meta.yaml'))
        # test cases for import prediction meta
        mir_root = self._mir_repo_root
        gen_folder = os.path.join(self._storage_root, 'gen')
        args = type('', (), {})()
        args.mir_root = mir_root
        args.label_storage_file = ids_file_path(mir_root)
        args.src_revs = ''
        args.dst_rev = 'a@import-task-0'
        args.index_file = self._idx_file
        args.ck_file = self._ck_file
        args.pred_dir = self._data_xml_path
        args.gt_dir = self._data_xml_path
        args.gen_abs = gen_folder
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'stop'
        args.anno_type = 'det-box'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo(self._mir_repo_root,
                         with_person_ignored=False,
                         with_annotations=True,
                         eval_class_ids_set={0, 1, 2})
        shutil.move(os.path.join(self._data_xml_path, 'meta.yaml'), os.path.join(self._data_xml_path, 'pred_meta.yaml'))

    def _check_repo(self,
                    repo_root: str,
                    with_person_ignored: bool,
                    with_annotations: bool,
                    task_new_types: dict = {},
                    task_new_types_added: bool = False,
                    eval_class_ids_set: Set[int] = set()):
        # check annotations.mir
        mir_annotations = mirpb.MirAnnotations()
        with open(os.path.join(repo_root, 'annotations.mir'), 'rb') as f:
            mir_annotations.ParseFromString(f.read())

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
        }
        if with_person_ignored:
            dict_image_annotations_expect = {
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'boxes': [{
                        'box': {
                            'x': 181,
                            'y': 127,
                            'w': 94,
                            'h': 67,
                            'rotate_angle': -0.02
                        },
                        'class_id': 1,
                        'cm': 'FP' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
                        'anno_quality': 0.75,
                        'tags': {
                            'difficult': '0',
                            'color': 'pink',
                            'pose': 'Unspecified'
                        }
                    }],
                    'img_class_ids': [1],
                },
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'boxes': [{
                        'box': {
                            'x': 104,
                            'y': 78,
                            'w': 272,
                            'h': 106,
                            'rotate_angle': 0.22
                        },
                        'class_id': 1,
                        'cm': 'TP' if eval_class_ids_set else 'NotSet',
                        'score': 0.5,
                        'anno_quality': 0.62,
                        'tags': {
                            'difficult': '0',
                            'color': 'white',
                            'pose': 'Frontal'
                        }
                    }, {
                        'index': 1,
                        'box': {
                            'x': 133,
                            'y': 88,
                            'w': 65,
                            'h': 36,
                            'rotate_angle': 0.02
                        },
                        'class_id': 1,
                        'cm': 'FP' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
                        'anno_quality': 0.75,
                        'tags': {
                            'difficult': '0',
                            'color': 'blue',
                            'pose': 'Left'
                        }
                    }],
                    'img_class_ids': [1],
                }
            }
        else:
            dict_image_annotations_expect = {
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
                    'boxes': [{
                        'box': {
                            'x': 181,
                            'y': 127,
                            'w': 94,
                            'h': 67,
                            'rotate_angle': -0.02
                        },
                        'class_id': 1,
                        'cm': 'IGNORED' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
                        'anno_quality': 0.75,
                        'tags': {
                            'difficult': '0',
                            'color': 'pink',
                            'pose': 'Unspecified'
                        }
                    }],
                    'img_class_ids': [1],
                },
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'boxes': [{
                        'box': {
                            'x': 104,
                            'y': 78,
                            'w': 272,
                            'h': 106,
                            'rotate_angle': 0.22
                        },
                        'class_id': 1,
                        'cm': 'TP' if eval_class_ids_set else 'NotSet',
                        'score': 0.5,
                        'anno_quality': 0.62,
                        'tags': {
                            'difficult': '0',
                            'color': 'white',
                            'pose': 'Frontal'
                        }
                    }, {
                        'index': 1,
                        'box': {
                            'x': 133,
                            'y': 88,
                            'w': 65,
                            'h': 36,
                            'rotate_angle': 0.02
                        },
                        'class_id': 1,
                        'cm': 'IGNORED' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
                        'anno_quality': 0.75,
                        'tags': {
                            'difficult': '0',
                            'color': 'blue',
                            'pose': 'Left'
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
                        'cm': 'IGNORED' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
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
                            'h': 50,
                            'rotate_angle': 0.12
                        },
                        'class_id': 2,
                        'cm': 'IGNORED' if eval_class_ids_set else 'NotSet',
                        'det_link_id': -1 if eval_class_ids_set else 0,
                        'score': -1.0,
                        'anno_quality': 0.35,
                        'tags': {
                            'difficult': '1',
                            'pose': 'Rear'
                        }
                    }],
                    'img_class_ids': [1, 2],
                }
            }
        mir_annotations_expected = mirpb.MirAnnotations()
        if with_annotations:
            ParseDict(
                {
                    'prediction': {
                        'image_annotations': dict_image_annotations_expect
                    },
                    'image_cks': dict_asset_cks_expected,
                }, mir_annotations_expected)

        try:
            self.assertEqual(mir_annotations_expected.prediction.image_annotations,
                             mir_annotations.prediction.image_annotations)
            self.assertEqual(mir_annotations_expected.image_cks, mir_annotations.image_cks)
            self.assertEqual(eval_class_ids_set, set(mir_annotations.prediction.eval_class_ids))
        except AssertionError as e:
            raise e

        # check keywords.mir and contexts.mir
        mir_keywords = mirpb.MirKeywords()
        mir_context = mirpb.MirContext()
        with open(os.path.join(repo_root, 'keywords.mir'), 'rb') as f:
            mir_keywords.ParseFromString(f.read())
        with open(os.path.join(repo_root, 'context.mir'), 'rb') as f:
            mir_context.ParseFromString(f.read())
        if with_annotations:
            if with_person_ignored:
                pred_gt_idx = {
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
                }
                dict_keywords_expect = {
                    'pred_idx': pred_gt_idx,
                    'gt_idx': pred_gt_idx,
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
                pred_gt_stats = {
                    'total_cnt': 3,
                    'positive_asset_cnt': 2,
                    'negative_asset_cnt': 0,
                    'class_ids_cnt': {
                        1: 2,
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
                }
                dict_context_expected = {
                    'images_cnt': 2,
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
                    'pred_stats': pred_gt_stats,
                    'gt_stats': pred_gt_stats,
                }
            else:
                pred_gt_idx = {
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
                }
                dict_keywords_expect = {
                    'pred_idx': pred_gt_idx,
                    'gt_idx': pred_gt_idx,
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
                pred_gt_stats = {
                    'total_cnt': 5,
                    'positive_asset_cnt': 2,
                    'negative_asset_cnt': 0,
                    'class_ids_cnt': {
                        1: 2,
                        2: 1,
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
                }
                dict_context_expected = {
                    'images_cnt': 2,
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
                    'pred_stats': pred_gt_stats,
                    'gt_stats': pred_gt_stats,
                }
            mir_keywords_expected = mirpb.MirKeywords()
            ParseDict(dict_keywords_expect, mir_keywords_expected)
            mir_context_expected = mirpb.MirContext()
            mir_context_expected.pred_stats.eval_class_ids[:] = eval_class_ids_set
            ParseDict(dict_context_expected, mir_context_expected)
            try:
                self.assertEqual(mir_keywords, mir_keywords_expected)
                self.assertEqual(mir_context, mir_context_expected)
            except AssertionError as e:
                raise e
        else:
            self.assertEqual(0, len(mir_keywords.pred_idx.cis))
            self.assertEqual(0, len(mir_context.pred_stats.class_ids_cnt))

        # check metadatas.mir
        mir_metadatas = mirpb.MirMetadatas()
        with open(os.path.join(repo_root, 'metadatas.mir'), 'rb') as f:
            mir_metadatas.ParseFromString(f.read())
        dict_metadatas = MessageToDict(mir_metadatas, preserving_proto_field_name=True)
        dict_metadatas_expect = {
            'attributes': {
                '430df22960b0f369318705800139fcc8ec38a3e4': {
                    'asset_type': 'AssetTypeImageJpeg',
                    'width': 500,
                    'height': 281,
                    'image_channels': 3
                },
                'a3008c032eb11c8d9ffcb58208a36682ee40900f': {
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
        self.assertTrue({'import-task-0', 'import-task-1', 'import-task-2', 'import-task-3'} & mir_tasks.tasks.keys())

        task = mir_tasks.tasks[mir_tasks.head_task_id]
        task_dict = MessageToDict(task, preserving_proto_field_name=True)
        self.assertEqual(task_dict.get('new_types', {}), task_new_types)
        self.assertEqual(task_dict.get('new_types_added', False), task_new_types_added)

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
        self._gt_idx_file = os.path.join(self._data_root, 'gt_idx.txt')
        self._ck_file = os.path.join(self._data_root, 'ck.tsv')
        self._data_img_path = os.path.join(self._data_root, 'img')
        os.makedirs(self._data_img_path)
        self._data_xml_path = os.path.join(self._data_root, 'xml')
        os.makedirs(self._data_xml_path)

        self._prepare_data(data_root=self._data_root,
                           idx_file=self._idx_file,
                           gt_idx_file=self._gt_idx_file,
                           ck_file=self._ck_file,
                           data_img_path=self._data_img_path,
                           data_xml_path=self._data_xml_path)

    def _prepare_data(self, data_root, idx_file, gt_idx_file, ck_file, data_img_path, data_xml_path):
        local_data_root = 'tests/assets'

        # Copy img files.
        img_files = ['2007_000032.jpg', '2007_000243.jpg']
        with open(idx_file, 'w') as idx_f, open(gt_idx_file, 'w') as gt_idx_f, open(ck_file, 'w') as ck_f:
            for file in img_files:
                src = os.path.join(local_data_root, file)
                dst = os.path.join(data_img_path, file)
                shutil.copyfile(src, dst)

                idx_f.writelines(dst + '\n')
                gt_idx_f.writelines(dst + '\n')
                ck_f.write(f"{dst}\tck0\n")

        # Copy xml files.
        xml_files = ['2007_000032.xml', '2007_000243.xml']
        for file in xml_files:
            src = os.path.join(local_data_root, file)
            dst = os.path.join(data_xml_path, file)
            shutil.copyfile(src, dst)

        # Copy meta file
        shutil.copyfile(os.path.join(local_data_root, 'pred_meta.yaml'), os.path.join(data_xml_path, 'pred_meta.yaml'))

    def _prepare_mir_repo(self):
        # init repo
        test_utils.mir_repo_init(self._mir_repo_root)
        # prepare branch a
        test_utils.mir_repo_create_branch(self._mir_repo_root, 'a')
