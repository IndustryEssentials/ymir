import logging
import os
import shutil
import unittest

from google.protobuf.json_format import MessageToDict

from mir.commands.merge import CmdMerge
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from mir.tools.errors import MirRuntimeError
import tests.utils as test_utils


class TestMergeCmd(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()

    def tearDown(self):
        self._deprepare_dirs()

    # protected: prepare env
    def _prepare_dirs(self):
        test_utils.remake_dirs(self._mir_root)

    def _deprepare_dirs(self):
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)

        # branches:
        #   a: a0, a1, a2, a3
        #   b: b0, b1, b2
        #   d: a0, d0, d1
        test_utils.mir_repo_create_branch(self._mir_root, "a")
        self._prepare_mir_branch_a()
        test_utils.mir_repo_create_branch(self._mir_root, "b")
        self._prepare_mir_branch_b()
        test_utils.mir_repo_create_branch(self._mir_root, "d")
        self._prepare_mir_branch_d()
        test_utils.mir_repo_checkout(self._mir_root, "master")

    def _prepare_mir_branch_a(self):
        """
        assets and keywords:
            a: a0(1), a1(1), a2(1), a3(1)
        all asset size set to (1000, 1000)
        """
        assets_and_keywords = {
            "a0": ([1], {
                "c0": "c1"
            }),
            "a1": ([1], {
                "c0": "c1"
            }),
            "a2": ([1], {
                "c0": "c1"
            }),
            "a3": ([1], {
                "c0": "c1"
            }),
        }
        test_utils.prepare_mir_branch(mir_root=self._mir_root,
                                      assets_and_keywords=assets_and_keywords,
                                      size=1000,
                                      branch_name_and_task_id="a",
                                      commit_msg="prepare_branch_merge_a")

    def _prepare_mir_branch_b(self):
        """
        assets and keywords:
            b: b0(2), b1(2), b2(2)
        all asset size set to (1100, 1100)
        """
        assets_and_keywords = {
            "b0": ([2], {
                "c0": "c2"
            }),
            "b1": ([2], {
                "c0": "c2"
            }),
            "b2": ([2], {
                "c0": "c2"
            }),
        }
        test_utils.prepare_mir_branch(mir_root=self._mir_root,
                                      assets_and_keywords=assets_and_keywords,
                                      size=1100,
                                      branch_name_and_task_id="b",
                                      commit_msg="prepare_branch_merge_b")

    def _prepare_mir_branch_d(self):
        """
        assets and keywords:
            d: a0(1, 2), d0(1, 4), d1(1, 4)
        all asset size set to (1300, 1300)
        """
        assets_and_keywords = {
            "a0": ([1, 2], {
                "c0": "c4"
            }),
            "d0": ([1, 4], {
                "c0": "c4"
            }),
            "d1": ([1, 4], {
                "c0": "c4"
            }),
        }
        test_utils.prepare_mir_branch(mir_root=self._mir_root,
                                      assets_and_keywords=assets_and_keywords,
                                      size=1300,
                                      branch_name_and_task_id="d",
                                      commit_msg="prepare_branch_merge_d")

    # protected: check
    def _check_result(self, expected_dict_metadatas=None, expected_dict_annotations=None):
        if expected_dict_metadatas:
            try:
                mir_metadatas = test_utils.read_mir_pb(os.path.join(self._mir_root, "metadatas.mir"),
                                                       mirpb.MirMetadatas)
                actual_dict_metadatas = MessageToDict(mir_metadatas, preserving_proto_field_name=True)
                self.assertEqual(expected_dict_metadatas, actual_dict_metadatas)
            except AssertionError as e:
                logging.info(f"e: {expected_dict_metadatas}")
                logging.info(f"a: {actual_dict_metadatas}")
                raise e

        if expected_dict_annotations:
            try:
                mir_annotations = test_utils.read_mir_pb(os.path.join(self._mir_root, "annotations.mir"),
                                                         mirpb.MirAnnotations)
                actual_dict_annotations = MessageToDict(mir_annotations,
                                                        preserving_proto_field_name=True,
                                                        use_integers_for_enums=True)
                self.assertEqual(expected_dict_annotations, actual_dict_annotations)
            except AssertionError as e:
                logging.info(f"e: {expected_dict_annotations}")
                logging.info(f"a: {actual_dict_annotations}")
                raise e

    # public: test cases
    def test_all(self):
        self._test_exclude_no_tvt_host_00()
        self._test_no_tvt_stop_00()
        self._test_tvt_guest_00()
        self._test_tvt_host_00()
        self._test_tvt_stop_01()

    # protected: test cases
    def _test_no_tvt_stop_00(self):
        """ a + b """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'b;a'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = '_test_no_tvt_stop_00@merge-task-id-s0'
        fake_args.strategy = 'stop'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check results
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": test_utils.generate_attribute_for_asset(1000, 1000),
                "a1": test_utils.generate_attribute_for_asset(1000, 1000),
                "a2": test_utils.generate_attribute_for_asset(1000, 1000),
                "a3": test_utils.generate_attribute_for_asset(1000, 1000),
                "b0": test_utils.generate_attribute_for_asset(1100, 1100),
                "b1": test_utils.generate_attribute_for_asset(1100, 1100),
                "b2": test_utils.generate_attribute_for_asset(1100, 1100),
            }
        }

        expected_pred = {
            'task_id': 'merge-task-id-s0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a0": test_utils.generate_annotations_for_asset([1], 100, 100, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.IGNORED),
                "b0": test_utils.generate_annotations_for_asset([2], 100, 100, cm=mirpb.ConfusionMatrixType.IGNORED),
                "b1": test_utils.generate_annotations_for_asset([2], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "b2": test_utils.generate_annotations_for_asset([2], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
            },
            'task_class_ids': [1, 2],
            'model': {},
            'eval_class_ids': [1, 2],
        }
        expected_gt = {
            'task_id': 'merge-task-id-s0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a0": test_utils.generate_annotations_for_asset([1], 100, 100, cm=mirpb.ConfusionMatrixType.FN),
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.FN),
                "b0": test_utils.generate_annotations_for_asset([2], 100, 100, cm=mirpb.ConfusionMatrixType.FN),
                "b1": test_utils.generate_annotations_for_asset([2], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "b2": test_utils.generate_annotations_for_asset([2], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
            },
            'task_class_ids': [1, 2],
        }
        expected_dict_annotations = {
            "prediction": expected_pred,
            'ground_truth': expected_gt,
            'image_cks': {
                'a0': {
                    'cks': {
                        'c0': 'c1',
                    }
                },
                'a1': {
                    'cks': {
                        'c0': 'c1',
                    }
                },
                'a2': {
                    'cks': {
                        'c0': 'c1',
                    }
                },
                'a3': {
                    'cks': {
                        'c0': 'c1',
                    }
                },
                'b0': {
                    'cks': {
                        'c0': 'c2',
                    }
                },
                'b1': {
                    'cks': {
                        'c0': 'c2',
                    }
                },
                'b2': {
                    'cks': {
                        'c0': 'c2',
                    }
                }
            }
        }
        self._check_result(expected_dict_metadatas, expected_dict_annotations)

    def _test_tvt_stop_01(self):
        """ abnormal case: with tvt flag assigned, strategy stop, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = "_test_tvt_stop_01@merge-task-id-s1"
        fake_args.strategy = 'stop'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        with self.assertRaises(MirRuntimeError) as ectx:
            merge_instance.run()
        self.assertEqual(ectx.exception.error_code, MirCode.RC_CMD_MERGE_ERROR)

    def _test_tvt_host_00(self):
        """ normal case: with tvt flag assigned, strategy host, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = '_test_tvt_host_00@merge-task-id-h0'
        fake_args.strategy = 'host'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a1": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "d0": test_utils.generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "d1": test_utils.generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
            }
        }

        expected_pred = {
            'task_id': 'merge-task-id-h0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a0": test_utils.generate_annotations_for_asset([1], 100, 100, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.IGNORED),
                "d0": test_utils.generate_annotations_for_asset([1, 4], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "d1": test_utils.generate_annotations_for_asset([1, 4], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
            },
            'task_class_ids': [1, 4],
            'model': {},
            'eval_class_ids': [1, 2, 4],
        }
        expected_gt = {
            'task_id': 'merge-task-id-h0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a0": test_utils.generate_annotations_for_asset([1], 100, 100, cm=mirpb.ConfusionMatrixType.FN),
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.FN),
                "d0": test_utils.generate_annotations_for_asset([1, 4], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "d1": test_utils.generate_annotations_for_asset([1, 4], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
            },
            'task_class_ids': [1, 4],
        }
        expected_dict_annotations = {
            "prediction": expected_pred,
            'ground_truth': expected_gt,
            'image_cks': {
                'a0': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a1': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a2': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a3': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'd0': {
                    'cks': {
                        'c0': 'c4'
                    }
                },
                'd1': {
                    'cks': {
                        'c0': 'c4'
                    }
                },
            },
        }

        self._check_result(expected_dict_metadatas, expected_dict_annotations)

    def _test_tvt_guest_00(self):
        """ normal case: with tvt flag assigned, strategy guest, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = '_test_tvt_guest_00@merge-task-id-g0'
        fake_args.strategy = 'guest'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": test_utils.generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "a1": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "d0": test_utils.generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "d1": test_utils.generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
            }
        }

        expected_pred = {
            'task_id': 'merge-task-id-g0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a0": test_utils.generate_annotations_for_asset([1, 2], 100, 100, cm=mirpb.ConfusionMatrixType.IGNORED),
                "d0": test_utils.generate_annotations_for_asset([1, 4], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "d1": test_utils.generate_annotations_for_asset([1, 4], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
            },
            'task_class_ids': [1, 2, 4],
            'model': {},
            'eval_class_ids': [1, 2, 4],
        }
        expected_gt = {
            'task_id': 'merge-task-id-g0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.FN),
                "a0": test_utils.generate_annotations_for_asset([1, 2], 100, 100, cm=mirpb.ConfusionMatrixType.FN),
                "d0": test_utils.generate_annotations_for_asset([1, 4], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "d1": test_utils.generate_annotations_for_asset([1, 4], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
            },
            'task_class_ids': [1, 2, 4],
        }
        expected_dict_annotations = {
            "prediction": expected_pred,
            'ground_truth': expected_gt,
            'image_cks': {
                'a0': {
                    'cks': {
                        'c0': 'c4'
                    }
                },
                'a1': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a2': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a3': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'd0': {
                    'cks': {
                        'c0': 'c4'
                    }
                },
                'd1': {
                    'cks': {
                        'c0': 'c4'
                    }
                },
            },
        }

        self._check_result(expected_dict_metadatas, expected_dict_annotations)

    def _test_exclude_no_tvt_host_00(self):
        """ a - d with host strategy """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a'
        fake_args.ex_src_revs = 'd'
        fake_args.dst_rev = '_test_exclude_no_tvt_host_00@merge-task-id-nth0'
        fake_args.strategy = 'host'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a1": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": test_utils.generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
            }
        }

        expected_pred = {
            'task_id': 'merge-task-id-nth0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.IGNORED),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.IGNORED),
            },
            'task_class_ids': [1],
            'eval_class_ids': [1],
        }
        expected_gt = {
            'task_id': 'merge-task-id-nth0',
            'type': mirpb.ObjectType.OT_DET_BOX,
            "image_annotations": {
                "a1": test_utils.generate_annotations_for_asset([1], 100, 200, cm=mirpb.ConfusionMatrixType.FN),
                "a2": test_utils.generate_annotations_for_asset([1], 100, 300, cm=mirpb.ConfusionMatrixType.FN),
                "a3": test_utils.generate_annotations_for_asset([1], 100, 400, cm=mirpb.ConfusionMatrixType.FN),
            },
            'task_class_ids': [1],
        }
        expected_dict_annotations = {
            "prediction": expected_pred,
            'ground_truth': expected_gt,
            'image_cks': {
                'a1': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a2': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
                'a3': {
                    'cks': {
                        'c0': 'c1'
                    }
                },
            }
        }

        self._check_result(expected_dict_metadatas, expected_dict_annotations)
