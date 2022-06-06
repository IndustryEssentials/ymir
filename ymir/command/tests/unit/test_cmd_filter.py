import multiprocessing as mp
import os
import shutil
from typing import Dict, List, Set, Tuple
import unittest

from google.protobuf import json_format

from mir.commands import filter as cmd_filter
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import utils as mir_utils
from mir.tools import mir_storage_ops
from mir.tools.code import MirCode
from mir.tools.mir_storage_ops import MirStorageOps

from tests import utils as test_utils

# Python 3.8 in macOS switches to the spawn start method in multiprocessing as default,
# this fix makes sure the same behaviour on both unix/mac system.
mp.set_start_method('fork')


class TestCmdFilter(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self.__prepare_dir(self._mir_root)
        test_utils.prepare_labels(mir_root=self._mir_root,
                                  names=['frisbee', 'type1', 'person', 'type3', 'cat', 'chair'])
        self.__prepare_mir_repo(self._mir_root)
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dir(self._mir_root)
        return super().tearDown()

    # private: prepare env
    def __prepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)
        os.makedirs(mir_root, exist_ok=True)

    def __deprepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)

    def __prepare_mir_repo(self, mir_root: str):
        test_utils.mir_repo_init(self._mir_root)

        metadatas_dict = {
            "attributes": {
                self.__asset_id(0): {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                self.__asset_id(1): {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                self.__asset_id(2): {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                self.__asset_id(3): {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                self.__asset_id(4): {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        annotations_dict = {
            "task_annotations": {
                "t0": {
                    "image_annotations": {
                        self.__asset_id(0):
                        self.__annotations_for_single_image(cis=[0, 1, 2, 3, 4, 5], cks=['a', 'b']),
                        self.__asset_id(1):
                        self.__annotations_for_single_image(cis=[4], cks=['a', 'c']),
                        self.__asset_id(2):
                        self.__annotations_for_single_image(cis=[3], cks=['b', 'c']),
                        self.__asset_id(3):
                        self.__annotations_for_single_image(cis=[2], cks=['a', 'b', 'c']),
                        self.__asset_id(4):
                        self.__annotations_for_single_image(cis=[0, 1], cks=[]),
                    }
                }
            },
            'head_task_id': 't0',
        }
        mir_annotations = mirpb.MirAnnotations()
        json_format.ParseDict(annotations_dict, mir_annotations)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData,
                                           task_id='t0',
                                           message='import')

        MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                      mir_branch='a',
                                      his_branch='master',
                                      mir_datas={
                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                          mirpb.MirStorage.MIR_ANNOTATIONS: mir_annotations,
                                      },
                                      task=task)

    @classmethod
    def __asset_id(cls, id: int) -> str:
        return f"a{id:03}"

    @classmethod
    def __asset_ids(cls, *ids: Tuple[int]) -> Set[str]:
        return {cls.__asset_id(id) for id in ids}

    @classmethod
    def __annotations_for_single_image(cls, cis: List[int], cks: List[str]) -> Dict[str, list]:
        annotations = []
        for idx, type_id in enumerate(cis):
            annotations.append({
                "index": idx,
                "box": {
                    "x": (100 * idx),
                    "y": 100,
                    "w": 100,
                    "h": 100
                },  # set to any values if you wish
                "score": 0.5,
                "class_id": type_id,
            })
        return {"annotations": annotations, 'customized_keywords': cks}

    # public: test cases
    def test_all(self):
        self.__test_cmd_filter_normal()

        # test for write lock
        pipe0 = mp.Pipe()
        pipe1 = mp.Pipe()
        process0 = mp.Process(target=self.__test_multiprocess, args=('mp0', pipe0[1]))
        process1 = mp.Process(target=self.__test_multiprocess, args=('mp1', pipe1[1]))
        process0.start()
        process0.join()
        process1.start()
        process1.join()
        self.assertEqual(MirCode.RC_OK, pipe0[0].recv())
        self.assertEqual(MirCode.RC_OK, pipe1[0].recv())

    def __test_cmd_filter_normal(self):
        self.__test_cmd_filter_normal_cases(in_cis='frisbee; person; ChAiR',  # 0; 2; 15
                                            ex_cis='Cat',  # 4
                                            in_cks='',
                                            ex_cks='',
                                            task_id='t1',
                                            expected_asset_ids=self.__asset_ids(3, 4))

        self.__test_cmd_filter_normal_cases(in_cis='',
                                            ex_cis='',
                                            in_cks='a;b',
                                            ex_cks='',
                                            task_id='t2',
                                            expected_asset_ids=self.__asset_ids(0, 1, 2, 3))

        self.__test_cmd_filter_normal_cases(in_cis='',
                                            ex_cis='',
                                            in_cks='a;b',
                                            ex_cks='z',
                                            task_id='t3',
                                            expected_asset_ids=self.__asset_ids(0, 1, 2, 3))

        self.__test_cmd_filter_normal_cases(in_cis='',
                                            ex_cis='',
                                            in_cks=' a; b ;',
                                            ex_cks='c',
                                            task_id='t4',
                                            expected_asset_ids=self.__asset_ids(0))

        self.__test_cmd_filter_normal_cases(in_cis='frisbee; person; CaT',
                                            ex_cis='',
                                            in_cks='',
                                            ex_cks='c',
                                            task_id='t5',
                                            expected_asset_ids=self.__asset_ids(0, 4))


    def __test_cmd_filter_normal_cases(self, in_cis: str, ex_cis: str, in_cks: str, ex_cks: str, task_id: str,
                                       expected_asset_ids: Set[str]):
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.in_cis = in_cis
        fake_args.ex_cis = ex_cis
        fake_args.in_cks = in_cks
        fake_args.ex_cks = ex_cks
        fake_args.src_revs = "a@t0"  # src branch name and base task id
        fake_args.dst_rev = f"{task_id}@{task_id}"
        fake_args.work_dir = ''
        cmd = cmd_filter.CmdFilter(fake_args)
        cmd_run_result = cmd.run()

        # check result
        self.assertEqual(MirCode.RC_OK, cmd_run_result)

        # check mir repo
        mir_metadatas = test_utils.read_mir_pb(os.path.join(self._mir_root, 'metadatas.mir'), mirpb.MirMetadatas)
        mir_annotations = test_utils.read_mir_pb(os.path.join(self._mir_root, 'annotations.mir'), mirpb.MirAnnotations)
        mir_keywords = test_utils.read_mir_pb(os.path.join(self._mir_root, 'keywords.mir'), mirpb.MirKeywords)
        mir_tasks = test_utils.read_mir_pb(os.path.join(self._mir_root, 'tasks.mir'), mirpb.MirTasks)
        self.assertEqual(expected_asset_ids, set(mir_metadatas.attributes.keys()))
        self.assertEqual(expected_asset_ids, set(mir_keywords.keywords.keys()))
        self.assertEqual(1, len(mir_annotations.task_annotations))
        self.assertEqual(expected_asset_ids, set(mir_annotations.task_annotations[task_id].image_annotations.keys()))
        self.assertEqual(1, len(mir_tasks.tasks))
        self.assertEqual(task_id, mir_tasks.head_task_id)
        self.assertEqual(task_id, mir_annotations.head_task_id)

        current_branch_name = mir_utils.mir_repo_head_name(self._mir_root)
        self.assertEqual(task_id, current_branch_name)

    def __test_multiprocess(self, dst_branch: str, child_conn):
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.in_cis = 'cat'
        fake_args.ex_cis = None
        fake_args.in_cks = None
        fake_args.ex_cks = None
        fake_args.src_revs = "a@t0"  # src branch name and base task id
        fake_args.dst_rev = f"{dst_branch}@t1"
        fake_args.work_dir = ''
        cmd = cmd_filter.CmdFilter(fake_args)
        cmd_run_result = cmd.run()
        child_conn.send(cmd_run_result)


if __name__ == "__main__":
    unittest.main()
