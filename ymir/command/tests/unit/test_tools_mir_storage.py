import logging
import os
import shutil
import unittest

import google.protobuf.json_format as pb_format
from google.protobuf.json_format import MessageToDict

from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage, mir_storage_ops, settings as mir_settings
from tests import utils as test_utils


class TestMirStorage(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self._prepare_dir()
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        return super().tearDown()

    # protected: misc
    def _prepare_dir(self):
        if os.path.isdir(self._mir_root):
            shutil.rmtree(self._mir_root)
        os.makedirs(self._mir_root, exist_ok=True)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_root)

    def _prepare_mir_pb(self, with_project: bool) -> tuple:
        mir_metadatas = mirpb.MirMetadatas()
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_context = mirpb.MirContext()
        mir_tasks = mirpb.MirTasks()

        dict_metadatas = {
            'attributes': {
                'a001': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                'a002': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                'a003': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
            }
        }
        pb_format.ParseDict(dict_metadatas, mir_metadatas)

        dict_annotations = {
            "prediction": {
                'task_id': 'mining-task-id',
                "image_annotations": {
                    "a001": {
                        'boxes': [{
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 1
                        }, {
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 2
                        }]
                    },
                    "a002": {
                        'boxes': [{
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 2
                        }, {
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 3
                        }]
                    },
                    "a003": {
                        'boxes': [{
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 3
                        }, {
                            'box': {
                                'x': 26,
                                'y': 189,
                                'w': 19,
                                'h': 50
                            },
                            'classId': 3
                        }]
                    }
                }
            }
        }
        pb_format.ParseDict(dict_annotations, mir_annotations)

        dict_context = {
            'images_cnt': 3,
            'pred_stats': {
                'total_obj_cnt': 6,
                'positive_asset_cnt': 3,
                'negative_asset_cnt': 0,
                'class_ids_cnt': {
                    1: 1,
                    2: 2,
                    3: 2,
                },
                'class_ids_mask_area': {
                    1: 0,
                    2: 0,
                    3: 0,
                },
                'class_ids_obj_cnt': {
                    1: 1,
                    2: 2,
                    3: 3,
                }
            },
            'gt_stats': {
                'negative_asset_cnt': 3
            }
        }
        pb_format.ParseDict(dict_context, mir_context)

        dict_tasks = {
            'tasks': {
                'mining-task-id': {
                    'type': 'TaskTypeMining',
                    'name': 'mining',
                    'task_id': 'mining-task-id',
                    'timestamp': '1624376173',
                    'model': {
                        'model_hash': 'abc123',
                        'mAP': 0.5,
                        'context': 'fake_context',
                        'stages': {},
                        'best_stage_name': '',
                    },
                    'evaluation': {
                        'config': {
                            'conf_thr': mir_settings.DEFAULT_EVALUATE_CONF_THR,
                            'iou_thrs_interval': mir_settings.DEFAULT_EVALUATE_IOU_THR,
                        },
                        'state': mirpb.EvaluationState.ES_NO_CLASS_IDS,
                    },
                }
            },
            'head_task_id': 'mining-task-id',
        }
        pb_format.ParseDict(dict_tasks, mir_tasks)

        return (mir_metadatas, mir_annotations, mir_keywords, mir_tasks, mir_context)

    # public: test cases
    def test_normal_00(self):
        """
        normal cases: no project context, commit twice
        """
        mir_metadatas, mir_annotations, _, mir_tasks, mir_context = self._prepare_mir_pb(with_project=False)
        mir_datas_expect = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
            mirpb.MirStorage.MIR_TASKS: mir_tasks,
        }
        mir_storage_list = mir_datas_expect.keys()
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations
                                                      },
                                                      task=mir_tasks.tasks[mir_tasks.head_task_id])
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms_list=mir_storage_list,
            as_dict=False,
        )
        actual_data = dict(zip(mir_storage_list, mir_datas))
        self.assertDictEqual(actual_data, mir_datas_expect)
        loaded_mir_context = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                               mir_branch='a',
                                                                               ms=mirpb.MirStorage.MIR_CONTEXT,
                                                                               mir_task_id='mining-task-id',
                                                                               as_dict=False)
        try:
            self.assertEqual(loaded_mir_context, mir_context)
        except AssertionError as e:
            logging.info(f"expected: {MessageToDict(mir_context, preserving_proto_field_name=True)}")
            logging.info(f"actual: {MessageToDict(loaded_mir_context, preserving_proto_field_name=True)}")
            raise e

        # add another commit a@t2, which has empty dataset
        task_2 = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeMining, task_id='t2', message='task-t2')
        task_2.evaluation.config.CopyFrom(mir_storage_ops.create_evaluate_config())
        task_2.evaluation.state = mirpb.EvaluationState.ES_NO_CLASS_IDS
        mir_tasks_2 = mirpb.MirTasks()
        mir_tasks_2.head_task_id = task_2.task_id
        mir_tasks_2.tasks[task_2.task_id].CopyFrom(task_2)
        mir_datas_expect_2 = {
            mirpb.MirStorage.MIR_METADATAS:
            mirpb.MirMetadatas(),
            mirpb.MirStorage.MIR_ANNOTATIONS:
            pb_format.ParseDict({
                "prediction": {
                    'task_id': 't2',
                },
                "ground_truth": {
                    'task_id': 't2',
                },
            }, mirpb.MirAnnotations()),
            mirpb.MirStorage.MIR_TASKS:
            mir_tasks_2,
        }

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='a',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mirpb.MirMetadatas(),
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations(),
                                                      },
                                                      task=task_2)
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms_list=mir_storage_list,
            as_dict=False,
        )
        actual_data = dict(zip(mir_storage_list, mir_datas))
        self.assertDictEqual(actual_data, mir_datas_expect)
        # previous a@mining-task-id remains unchanged
        mir_datas = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='t2',
            ms_list=mir_storage_list,
            as_dict=False,
        )
        actual_data = dict(zip(mir_storage_list, mir_datas))
        print(f"actual_data: {actual_data}")
        print(f"mir_datas_expect_2: {mir_datas_expect_2}")
        self.assertDictEqual(actual_data, mir_datas_expect_2)

        actual_contents_list = mir_storage_ops.MirStorageOps.load_multiple_storages(
            mir_root=self._mir_root,
            mir_branch='a',
            mir_task_id='mining-task-id',
            ms_list=mir_storage.get_all_mir_storage(),
            as_dict=False)
        self.assertEqual(len(actual_contents_list), 5)

    def test_normal_01(self):
        mir_metadatas, mir_annotations, mir_keywords, mir_tasks, mir_context = self._prepare_mir_pb(with_project=True)

        mir_datas_expect = {
            mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
            mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
        }
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas=mir_datas_expect,
                                                      task=mir_tasks.tasks[mir_tasks.head_task_id])
        loaded_mir_context = mir_storage_ops.MirStorageOps.load_single_storage(mir_root=self._mir_root,
                                                                               mir_branch='a',
                                                                               ms=mirpb.MirStorage.MIR_CONTEXT,
                                                                               mir_task_id='mining-task-id',
                                                                               as_dict=False)
        try:
            self.assertEqual(loaded_mir_context, mir_context)
        except AssertionError as e:
            logging.info(f"expected: {mir_context}")
            logging.info(f"actual: {loaded_mir_context}")
            raise e
