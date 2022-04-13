import logging
import os
import shutil
from typing import Dict, List, Tuple
import unittest

from google.protobuf.json_format import MessageToDict, ParseDict

from mir.commands.merge import CmdMerge
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops
from mir.tools.code import MirCode
import tests.utils as test_utils


class TestMergeCmd(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()

    def tearDown(self):
        self._deprepare_dirs()
        pass

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
        # test_utils.mir_repo_create_branch(self._mir_root, "c")
        # self._prepare_mir_branch_c()
        test_utils.mir_repo_create_branch(self._mir_root, "d")
        self._prepare_mir_branch_d()
        # test_utils.mir_repo_create_branch(self._mir_root, "e")
        # self._prepare_mir_branch_e()
        test_utils.mir_repo_checkout(self._mir_root, "master")

    @staticmethod
    def _generate_attribute_for_asset(width: int, height: int, tvt_type: int = mirpb.TvtTypeUnknown) -> dict:
        if tvt_type == mirpb.TvtTypeUnknown:
            return {'asset_type': 'AssetTypeImageJpeg', 'width': width, 'height': height, 'image_channels': 3}
        else:
            return {
                'asset_type': 'AssetTypeImageJpeg',
                'width': width,
                'height': height,
                'image_channels': 3,
                "tvt_type": mirpb.TvtType.Name(tvt_type)
            }

    @staticmethod
    def _generate_annotations_for_asset(type_ids: List[int], x: int, y: int):
        annotations_list = []
        for idx, type_id in enumerate(type_ids):
            annotations_list.append({
                'class_id': type_id,
                'box': {
                    'x': idx * 100 + x,
                    'y': y,
                    'w': 50,
                    'h': 50
                },
            })
        return {'annotations': annotations_list}

    @staticmethod
    def _generate_keywords_for_asset(predefined: List[int], customized: List[str]):
        return {'predifined_keyids': predefined, 'customized_keywords': customized}

    @staticmethod
    def _generate_task(task_id: str, name: str, type: int, timestamp: int):
        return {
            'type': type,
            'name': name,
            'task_id': task_id,
            'timestamp': timestamp,
            'model': {
                'model_hash': 'model_hash'
            }
        }

    def _prepare_mir_branch(self, assets_and_keywords: Dict[str, Tuple[List[int], List[str]]], size: int,
                            branch_name_and_task_id: str, commit_msg: str):
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_metadatas = mirpb.MirMetadatas()

        dict_metadatas = {'attributes': {}}
        for asset_id in assets_and_keywords:
            dict_metadatas["attributes"][asset_id] = TestMergeCmd._generate_attribute_for_asset(size, size)
        ParseDict(dict_metadatas, mir_metadatas)

        image_annotations = {}
        for asset_idx, (asset_id, keywords_pair) in enumerate(assets_and_keywords.items()):
            image_annotations[asset_id] = TestMergeCmd._generate_annotations_for_asset(type_ids=keywords_pair[0],
                                                                                       x=100,
                                                                                       y=(asset_idx + 1) * 100)
        dict_annotations = {
            "task_annotations": {
                branch_name_and_task_id: {
                    "image_annotations": image_annotations
                }
            },
            'head_task_id': branch_name_and_task_id
        }
        ParseDict(dict_annotations, mir_annotations)

        dict_keywords = {"keywords": {}}
        for asset_id, keywords_pair in assets_and_keywords.items():
            dict_keywords["keywords"][asset_id] = TestMergeCmd._generate_keywords_for_asset(
                keywords_pair[0], keywords_pair[1])
        ParseDict(dict_keywords, mir_keywords)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskTypeMining,
                                           task_id=branch_name_and_task_id,
                                           message=commit_msg)
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch=branch_name_and_task_id,
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    def _prepare_mir_branch_a(self):
        """
        assets and keywords:
            a: a0(1), a1(1), a2(1), a3(1)
        all asset size set to (1000, 1000)
        """
        assets_and_keywords = {
            "a0": ([1], ["c0", "c1"]),
            "a1": ([1], ["c0", "c1"]),
            "a2": ([1], ["c0", "c1"]),
            "a3": ([1], ["c0", "c1"]),
        }
        self._prepare_mir_branch(assets_and_keywords=assets_and_keywords,
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
            "b0": ([2], ["c0", "c2"]),
            "b1": ([2], ["c0", "c2"]),
            "b2": ([2], ["c0", "c2"]),
        }
        self._prepare_mir_branch(assets_and_keywords=assets_and_keywords,
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
            "a0": ([1, 2], ["c0", "c1", "c2"]),
            "d0": ([1, 4], ["c0", "c1", "c4"]),
            "d1": ([1, 4], ["c0", "c1", "c4"]),
        }
        self._prepare_mir_branch(assets_and_keywords=assets_and_keywords,
                                 size=1300,
                                 branch_name_and_task_id="d",
                                 commit_msg="prepare_branch_merge_d")

    # protected: check
    def _check_result(self,
                      expected_dict_metadatas=None,
                      expected_dict_annotations=None,
                      expected_dict_keywords=None):
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
                actual_dict_annotations = MessageToDict(mir_annotations, preserving_proto_field_name=True)
                self.assertEqual(expected_dict_annotations, actual_dict_annotations)
            except AssertionError as e:
                logging.info(f"e: {expected_dict_annotations}")
                logging.info(f"a: {actual_dict_annotations}")
                raise e

        if expected_dict_keywords:
            mir_keywords = test_utils.read_mir_pb(os.path.join(self._mir_root, "keywords.mir"), mirpb.MirKeywords)
            actual_dict_keywords = MessageToDict(mir_keywords, preserving_proto_field_name=True)
            for asset_id, expected_keywords in expected_dict_keywords["keywords"].items():
                actual_keywords = actual_dict_keywords["keywords"][asset_id]
                try:
                    self.assertEqual(set(expected_keywords["predifined_keyids"]),
                                     set(actual_keywords["predifined_keyids"]))
                except AssertionError as e:
                    logging.info(f"e: {expected_keywords}")
                    logging.info(f"a: {actual_keywords}")
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
        fake_args.dst_rev = '_test_no_tvt_stop_00@merge-task-id'
        fake_args.strategy = 'stop'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check results
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": TestMergeCmd._generate_attribute_for_asset(1000, 1000),
                "a1": TestMergeCmd._generate_attribute_for_asset(1000, 1000),
                "a2": TestMergeCmd._generate_attribute_for_asset(1000, 1000),
                "a3": TestMergeCmd._generate_attribute_for_asset(1000, 1000),
                "b0": TestMergeCmd._generate_attribute_for_asset(1100, 1100),
                "b1": TestMergeCmd._generate_attribute_for_asset(1100, 1100),
                "b2": TestMergeCmd._generate_attribute_for_asset(1100, 1100),
            }
        }

        expected_dict_annotations = {
            "task_annotations": {
                "merge-task-id": {
                    "image_annotations": {
                        "a0": TestMergeCmd._generate_annotations_for_asset([1], 100, 100),
                        "a1": TestMergeCmd._generate_annotations_for_asset([1], 100, 200),
                        "a2": TestMergeCmd._generate_annotations_for_asset([1], 100, 300),
                        "a3": TestMergeCmd._generate_annotations_for_asset([1], 100, 400),
                        "b0": TestMergeCmd._generate_annotations_for_asset([2], 100, 100),
                        "b1": TestMergeCmd._generate_annotations_for_asset([2], 100, 200),
                        "b2": TestMergeCmd._generate_annotations_for_asset([2], 100, 300),
                    }
                }
            },
            'head_task_id': 'merge-task-id',
        }

        expected_dict_keywords = {
            "keywords": {
                "a0": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a1": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a2": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a3": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "b0": TestMergeCmd._generate_keywords_for_asset([2], ["c0", "c2"]),
                "b1": TestMergeCmd._generate_keywords_for_asset([2], ["c0", "c2"]),
                "b2": TestMergeCmd._generate_keywords_for_asset([2], ["c0", "c2"]),
            }
        }
        self._check_result(expected_dict_metadatas, expected_dict_annotations, expected_dict_keywords)

    def _test_tvt_stop_01(self):
        """ abnormal case: with tvt flag assigned, strategy stop, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = "_test_tvt_stop_01@merge-task-id"
        fake_args.strategy = 'stop'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_CMD_MERGE_ERROR, ret)

    def _test_tvt_host_00(self):
        """ normal case: with tvt flag assigned, strategy host, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = '_test_tvt_host_00@merge-task-id'
        fake_args.strategy = 'host'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a1": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "d0": TestMergeCmd._generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "d1": TestMergeCmd._generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
            }
        }

        expected_dict_annotations = {
            "task_annotations": {
                "merge-task-id": {
                    "image_annotations": {
                        "a0": TestMergeCmd._generate_annotations_for_asset([1], 100, 100),
                        "a1": TestMergeCmd._generate_annotations_for_asset([1], 100, 200),
                        "a2": TestMergeCmd._generate_annotations_for_asset([1], 100, 300),
                        "a3": TestMergeCmd._generate_annotations_for_asset([1], 100, 400),
                        "d0": TestMergeCmd._generate_annotations_for_asset([1, 4], 100, 200),
                        "d1": TestMergeCmd._generate_annotations_for_asset([1, 4], 100, 300),
                    }
                }
            },
            'head_task_id': 'merge-task-id',
        }

        expected_dict_keywords = {
            "keywords": {
                "a0": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a1": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a2": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a3": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "d0": TestMergeCmd._generate_keywords_for_asset([1, 4], ["c0", "c1", "c4"]),
                "d1": TestMergeCmd._generate_keywords_for_asset([1, 4], ["c0", "c1", "c4"]),
            }
        }
        self._check_result(expected_dict_metadatas, expected_dict_annotations, expected_dict_keywords)

    def _test_tvt_guest_00(self):
        """ normal case: with tvt flag assigned, strategy guest, a + d, have joint assets """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a;va:d'
        fake_args.ex_src_revs = ''
        fake_args.dst_rev = '_test_tvt_guest_00@merge-task-id'
        fake_args.strategy = 'guest'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a0": TestMergeCmd._generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "a1": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "d0": TestMergeCmd._generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
                "d1": TestMergeCmd._generate_attribute_for_asset(1300, 1300, tvt_type=mirpb.TvtTypeValidation),
            }
        }

        expected_dict_annotations = {
            "task_annotations": {
                "merge-task-id": {
                    "image_annotations": {
                        "a1": TestMergeCmd._generate_annotations_for_asset([1], 100, 200),
                        "a2": TestMergeCmd._generate_annotations_for_asset([1], 100, 300),
                        "a3": TestMergeCmd._generate_annotations_for_asset([1], 100, 400),
                        "a0": TestMergeCmd._generate_annotations_for_asset([1, 2], 100, 100),
                        "d0": TestMergeCmd._generate_annotations_for_asset([1, 4], 100, 200),
                        "d1": TestMergeCmd._generate_annotations_for_asset([1, 4], 100, 300),
                    }
                }
            },
            'head_task_id': 'merge-task-id',
        }

        expected_dict_keywords = {
            "keywords": {
                "a0": TestMergeCmd._generate_keywords_for_asset([1, 2], ["c0", "c1", "c2"]),
                "a1": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a2": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a3": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "d0": TestMergeCmd._generate_keywords_for_asset([1, 4], ["c0", "c1", "c4"]),
                "d1": TestMergeCmd._generate_keywords_for_asset([1, 4], ["c0", "c1", "c4"]),
            }
        }

        self._check_result(expected_dict_metadatas, expected_dict_annotations, expected_dict_keywords)

    def _test_exclude_no_tvt_host_00(self):
        """ a - d with host strategy """
        mir_root = self._mir_root
        fake_args = type('', (), {})()
        fake_args.mir_root = mir_root
        fake_args.src_revs = 'tr:a'
        fake_args.ex_src_revs = 'd'
        fake_args.dst_rev = '_test_exclude_no_tvt_host_00@merge-task-id'
        fake_args.strategy = 'host'
        fake_args.work_dir = ''
        merge_instance = CmdMerge(fake_args)
        ret = merge_instance.run()

        # check result
        self.assertEqual(MirCode.RC_OK, ret)

        expected_dict_metadatas = {
            "attributes": {
                "a1": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a2": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
                "a3": TestMergeCmd._generate_attribute_for_asset(1000, 1000, tvt_type=mirpb.TvtTypeTraining),
            }
        }

        expected_dict_annotations = {
            "task_annotations": {
                "merge-task-id": {
                    "image_annotations": {
                        "a1": TestMergeCmd._generate_annotations_for_asset([1], 100, 200),
                        "a2": TestMergeCmd._generate_annotations_for_asset([1], 100, 300),
                        "a3": TestMergeCmd._generate_annotations_for_asset([1], 100, 400),
                    }
                }
            },
            'head_task_id': 'merge-task-id',
        }

        expected_dict_keywords = {
            "keywords": {
                "a1": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a2": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
                "a3": TestMergeCmd._generate_keywords_for_asset([1], ["c0", "c1"]),
            }
        }

        self._check_result(expected_dict_metadatas, expected_dict_annotations, expected_dict_keywords)
