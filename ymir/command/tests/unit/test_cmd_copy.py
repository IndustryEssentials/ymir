import os
import shutil
from typing import List, Set
import unittest

from mir.commands import copy
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage, mir_storage_ops
from mir.tools.code import MirCode

from tests import utils as test_utils


class TestCmdCopy(unittest.TestCase):
    # lifecycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._mir_root = os.path.join(self._test_root, 'one')
        self._src_mir_root = os.path.join(self._test_root, 'another')
        self._work_dir = os.path.join(self._test_root, 'work_dir')

    def setUp(self) -> None:
        self.__prepare_dir()
        self.__prepare_src_mir()
        test_utils.prepare_labels(mir_root=self._src_mir_root, names=['a', 'b', 'c', 'd'])
        self.__prepare_mir()
        test_utils.prepare_labels(mir_root=self._mir_root, names=['a', 'c1,c', 'b', 'e'])
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dir()
        return super().tearDown()

    # private: prepare
    def __prepare_dir(self):
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._mir_root)
        test_utils.remake_dirs(self._src_mir_root)
        test_utils.remake_dirs(self._work_dir)

    def __deprepare_dir(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def __prepare_mir(self):
        test_utils.mir_repo_init(self._mir_root)

    def __prepare_src_mir(self):
        test_utils.mir_repo_init(self._src_mir_root)

        test_utils.mir_repo_create_branch(self._src_mir_root, 'a')
        self.__prepare_src_mir_branch_a(task_id='t0')
        self.__prepare_src_mir_branch_a(task_id='t1', eval_class_ids=[0, 1])

    def __prepare_src_mir_branch_a(self, task_id: str, eval_class_ids: List[int] = []) -> None:
        mir_metadatas = mirpb.MirMetadatas()
        mir_metadatas.attributes['asset0']
        mir_metadatas.attributes['asset0'].width = 30
        mir_metadatas.attributes['asset0'].height = 30
        mir_metadatas.attributes['asset1']
        mir_metadatas.attributes['asset1'].width = 30
        mir_metadatas.attributes['asset1'].height = 30

        mir_annotations = mirpb.MirAnnotations()
        mir_annotations.prediction.image_annotations['asset0'].CopyFrom(
            self.__create_image_annotations(type_ids=[1, 2, 3]))
        mir_annotations.prediction.image_annotations['asset1'].CopyFrom(
            self.__create_image_annotations(type_ids=[3]))
        mir_annotations.prediction.eval_class_ids[:] = eval_class_ids

        model_meta = mirpb.ModelMeta(mean_average_precision=0.3)
        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeTraining,
                                           task_id=task_id,
                                           message='training',
                                           model_meta=model_meta)

        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._src_mir_root,
                                                      mir_branch='a',
                                                      his_branch='a',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                                      },
                                                      task=task)

    def __create_image_annotations(self, type_ids: List[int]) -> mirpb.SingleImageAnnotations:
        single_image_annotations = mirpb.SingleImageAnnotations()
        for idx, type_id in enumerate(type_ids):
            annotation = mirpb.ObjectAnnotation()
            annotation.index = idx
            annotation.class_id = type_id
            single_image_annotations.boxes.append(annotation)
        return single_image_annotations

    # private: check results
    def __check_results(self, dst_branch: str, dst_tid: str, ignore_unknown_types: bool, drop_annotations: bool,
                        eval_class_ids_set: Set[int] = set()):
        [mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
         _] = mir_storage_ops.MirStorageOps.load_multiple_storages(
             mir_root=self._mir_root,
             mir_branch=dst_branch,
             mir_task_id='',
             ms_list=mir_storage.get_all_mir_storage(),
             as_dict=False,
         )
        metadatas_keys = set(mir_metadatas.attributes.keys())
        self.assertEqual({'asset0', 'asset1'}, metadatas_keys)

        if drop_annotations:
            self.assertEqual(0, len(mir_annotations.prediction.image_annotations))
        else:
            asset0_idx_ids = {
                annotation.index: annotation.class_id
                for annotation in mir_annotations.prediction.image_annotations['asset0'].boxes
            }
            asset1_idx_ids = {
                annotation.index: annotation.class_id
                for annotation in mir_annotations.prediction.image_annotations['asset1'].boxes
            }
            self.assertEqual({0: 2, 1: 1}, asset0_idx_ids)
            self.assertEqual({}, asset1_idx_ids)
        self.assertEqual(eval_class_ids_set, set(mir_annotations.prediction.eval_class_ids))

        mAP = mir_tasks.tasks[dst_tid].model.mean_average_precision
        self.assertTrue(mAP > 0.29999 and mAP < 0.30001)  # it's actually 0.3

    # public: test cases
    def test_normal_00(self):
        # case 0
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.data_mir_root = self._src_mir_root
        fake_args.data_src_revs = 'a@t0'
        fake_args.dst_rev = 'b@t1'
        fake_args.work_dir = self._work_dir
        fake_args.ignore_unknown_types = True
        fake_args.drop_annotations = False
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()

        # check result
        self.assertEqual(MirCode.RC_OK, return_code)
        self.__check_results(dst_branch='b', dst_tid='t1', ignore_unknown_types=True, drop_annotations=False)

        # case 1
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.data_mir_root = self._src_mir_root
        fake_args.data_src_revs = 'a@t0'
        fake_args.dst_rev = 'b@t2'
        fake_args.work_dir = self._work_dir
        fake_args.ignore_unknown_types = True
        fake_args.drop_annotations = True
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()

        # check result
        self.assertEqual(MirCode.RC_OK, return_code)
        self.__check_results(dst_branch='b', dst_tid='t2', ignore_unknown_types=True, drop_annotations=True)

        # run cmd: abnormal cases
        fake_args = type('', (), {})()
        fake_args.mir_root = ''
        fake_args.data_mir_root = ''
        fake_args.data_src_revs = 'a@t0'
        fake_args.dst_rev = 'b@t1'
        fake_args.work_dir = self._work_dir
        fake_args.ignore_unknown_types = True
        fake_args.drop_annotations = False
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()
        self.assertNotEqual(MirCode.RC_OK, return_code)

        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root + 'fake'
        fake_args.data_mir_root = self._src_mir_root + 'fake'
        fake_args.data_src_revs = 'a@t0'
        fake_args.dst_rev = 'b@t1'
        fake_args.work_dir = self._work_dir
        fake_args.ignore_unknown_types = True
        fake_args.drop_annotations = False
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()
        self.assertNotEqual(MirCode.RC_OK, return_code)
        
    def test_normal_01(self) -> None:
        # test cases for pred meta
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.data_mir_root = self._src_mir_root
        fake_args.data_src_revs = 'a@t1'
        fake_args.dst_rev = 'b@t1'
        fake_args.work_dir = self._work_dir
        fake_args.ignore_unknown_types = True
        fake_args.drop_annotations = False
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()
        self.assertEqual(MirCode.RC_OK, return_code)
        self.__check_results(dst_branch='b', dst_tid='t1', ignore_unknown_types=True, drop_annotations=False,
                             eval_class_ids_set={0, 2})
