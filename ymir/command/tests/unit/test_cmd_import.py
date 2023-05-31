import json
import logging
import os
import shutil
import unittest
from unittest import mock
import zipfile

from mir.commands.import_dataset import CmdImport
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.class_ids import ids_file_path
from mir.tools.code import MirCode
from mir.tools.eval import det_eval_voc, sem_seg_eval_mm, ins_seg_eval_coco
from mir.tools.mir_storage_ops import MirStorageOps
from tests import utils as test_utils


_orig_det_eval_func = det_eval_voc.evaluate
_orig_sem_seg_eval_func = sem_seg_eval_mm.evaluate
_orig_ins_seg_eval_func = ins_seg_eval_coco.evaluate


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

    def tearDown(self) -> None:
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)

    # protected: mocked funcs
    def _mock_det_eval(*args, **kwargs):
        return _orig_det_eval_func(*args, **kwargs)

    def _mock_sem_seg_eval(*args, **kwargs):
        return _orig_sem_seg_eval_func(*args, **kwargs)

    def _mock_ins_seg_eval(*args, **kwargs):
        return _orig_ins_seg_eval_func(*args, **kwargs)

    # public: test cases
    @mock.patch('mir.tools.eval.det_eval_voc.evaluate', side_effect=_mock_det_eval)
    def test_import_detbox_00(self, eval_mock):
        # test cases for det-box-voc import
        # normal
        mir_root = self._mir_repo_root
        gen_folder = os.path.join(self._storage_root, 'gen')
        args = type('', (), {})()
        args.mir_root = mir_root
        args.label_storage_file = ids_file_path(mir_root)
        args.src_revs = ''
        args.dst_rev = 'a@import_detbox_00'
        args.asset_abs = self._idx_file
        args.pred_abs = self._data_xml_path
        args.gt_abs = self._data_xml_path
        args.gen_abs = gen_folder
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'stop'
        args.anno_type_fmt = 'det:voc'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertFalse(eval_mock.called)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_detbox_00',
                                 expected_file_name='expected_import_detbox_00.json')

        # not write person label
        test_utils.prepare_labels(mir_root=self._mir_repo_root, names=['cat', 'airplane,aeroplane'])

        # ignore unknown types
        args.unknown_types_strategy = 'ignore'
        args.dst_rev = 'a@import_detbox_01'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_detbox_01',
                                 expected_file_name='expected_import_detbox_01.json')

        # add unknown types
        args.unknown_types_strategy = 'add'
        args.dst_rev = 'a@import_detbox_02'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_detbox_02',
                                 expected_file_name='expected_import_detbox_02.json')

        # have no annotations
        args.pred_abs = None
        args.gt_abs = None
        args.unknown_types_strategy = 'stop'
        args.dst_rev = 'a@import_detbox_03'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_detbox_03',
                                 expected_file_name='expected_import_detbox_03.json')

    @mock.patch('mir.tools.eval.det_eval_voc.evaluate', side_effect=_mock_det_eval)
    def test_import_detbox_01(self, eval_mock):
        """
        import detection dataset with pred, pred meta.yaml and gt
        Expect: cmd returns ok, result ok, det_eval_voc called
        """
        # test cases for import prediction meta
        shutil.move(os.path.join(self._data_xml_path, 'pred_meta.yaml'), os.path.join(self._data_xml_path, 'meta.yaml'))

        mir_root = self._mir_repo_root
        gen_folder = os.path.join(self._storage_root, 'gen')
        args = type('', (), {})()
        args.mir_root = mir_root
        args.label_storage_file = ids_file_path(mir_root)
        args.src_revs = ''
        args.dst_rev = 'a@import_detbox_10'
        args.asset_abs = self._idx_file
        args.pred_abs = self._data_xml_path
        args.gt_abs = self._data_xml_path
        args.gen_abs = gen_folder
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'stop'
        args.anno_type_fmt = 'det:voc'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertTrue(eval_mock.called)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_detbox_10',
                                 expected_file_name='expected_import_detbox_10.json')
        shutil.move(os.path.join(self._data_xml_path, 'meta.yaml'), os.path.join(self._data_xml_path, 'pred_meta.yaml'))

    @mock.patch('mir.tools.eval.sem_seg_eval_mm.evaluate', side_effect=_mock_sem_seg_eval)
    def test_import_semantic_seg_00(self, eval_mock) -> None:
        """
        import semantic segmentation dataset with pred, pred meta.yaml and gt
        Expect: cmd returns ok, sem_seg_eval_mm called
        """
        # test cases for import prediction meta
        shutil.move(os.path.join(self._data_xml_path, 'pred_meta.yaml'), os.path.join(self._data_xml_path, 'meta.yaml'))

        args = type('', (), {})()
        args.mir_root = self._mir_repo_root
        args.label_storage_file = ids_file_path(self._mir_repo_root)
        args.src_revs = ''
        args.dst_rev = 'a@import_semantic_seg_01'
        args.asset_abs = self._idx_file
        args.pred_abs = self._data_xml_path
        args.gt_abs = self._data_xml_path
        args.gen_abs = os.path.join(self._storage_root, 'gen')
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'add'
        args.anno_type_fmt = 'sem-seg:coco'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertTrue(eval_mock.called)

        shutil.move(os.path.join(self._data_xml_path, 'meta.yaml'), os.path.join(self._data_xml_path, 'pred_meta.yaml'))

    @mock.patch('mir.tools.eval.sem_seg_eval_mm.evaluate', side_effect=_mock_sem_seg_eval)
    def test_import_semantic_seg_01(self, eval_mock) -> None:
        """
        import semantic segmentation dataset with gt, without pred and pred meta.yaml
        Expect: cmd returns ok, sem_seg_eval_mm not called, result correct
        """
        args = type('', (), {})()
        args.mir_root = self._mir_repo_root
        args.label_storage_file = ids_file_path(self._mir_repo_root)
        args.src_revs = ''
        args.dst_rev = 'a@import_semantic_seg_01'
        args.asset_abs = self._data_root
        args.pred_abs = ''
        args.gt_abs = self._data_xml_path
        args.gen_abs = os.path.join(self._storage_root, 'gen')
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'add'
        args.anno_type_fmt = 'sem-seg:coco'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertFalse(eval_mock.called)
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='a',
                                 mir_task_id='import_semantic_seg_01',
                                 expected_file_name='expected_import_semantic_seg_01.json')

    @mock.patch('mir.tools.eval.sem_seg_eval_mm.evaluate', side_effect=_mock_sem_seg_eval)
    def test_import_semantic_seg_02(self, eval_mock) -> None:
        """
        import semantic segmentation dataset ZIP FILE with gt, without pred and pred meta.yaml
        Expect: cmd returns ok, sem_seg_eval_mm not called, result correct
        """
        args = type('', (), {})()
        args.mir_root = self._mir_repo_root
        args.label_storage_file = ids_file_path(self._mir_repo_root)
        args.src_revs = ''
        args.dst_rev = 'b@import_semantic_seg_01'
        args.asset_abs = os.path.join(self._data_root, 'dataset.zip')
        args.pred_abs = ''
        args.gt_abs = ''
        args.gen_abs = os.path.join(self._storage_root, 'gen')
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'add'
        args.anno_type_fmt = 'sem-seg:coco'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertFalse(eval_mock.called)
        # used the same data as expected_import_semantic_seg_01
        self._check_repo_by_file(mir_root=self._mir_repo_root,
                                 mir_branch='b',
                                 mir_task_id='import_semantic_seg_01',
                                 expected_file_name='expected_import_semantic_seg_01.json')
        self.assertTrue(os.path.isfile(args.asset_abs))  # check file exists after import

    @mock.patch('mir.tools.eval.ins_seg_eval_coco.evaluate', side_effect=_mock_ins_seg_eval)
    def test_import_instance_seg_00(self, eval_mock) -> None:
        """
        import instance segmentation dataset with pred, pred meta.yaml and gt
        Expect: cmd returns ok, ins_seg_eval_coco called
        """
        # test cases for import prediction meta
        shutil.move(os.path.join(self._data_xml_path, 'pred_meta.yaml'), os.path.join(self._data_xml_path, 'meta.yaml'))

        args = type('', (), {})()
        args.mir_root = self._mir_repo_root
        args.label_storage_file = ids_file_path(self._mir_repo_root)
        args.src_revs = ''
        args.dst_rev = 'a@import_semantic_seg_01'
        args.asset_abs = self._idx_file
        args.pred_abs = self._data_xml_path
        args.gt_abs = self._data_xml_path
        args.gen_abs = os.path.join(self._storage_root, 'gen')
        args.work_dir = self._work_dir
        args.unknown_types_strategy = 'add'
        args.anno_type_fmt = 'ins-seg:coco'
        importing_instance = CmdImport(args)
        ret = importing_instance.run()
        self.assertEqual(ret, MirCode.RC_OK)
        self.assertTrue(eval_mock.called)

        shutil.move(os.path.join(self._data_xml_path, 'meta.yaml'), os.path.join(self._data_xml_path, 'pred_meta.yaml'))

    def _check_repo_by_file(self, mir_root: str, mir_branch: str, mir_task_id: str, expected_file_name: str) -> None:
        with open(os.path.join('tests', 'assets', expected_file_name), 'r') as f:
            expected_dict = json.loads(f.read())
            test_utils.convert_dict_str_keys_to_int(expected_dict)

        mm, ma, mk, mc = MirStorageOps.load_multiple_storages(
            mir_root=mir_root,
            mir_branch=mir_branch,
            mir_task_id=mir_task_id,
            ms_list=[mirpb.MIR_METADATAS, mirpb.MIR_ANNOTATIONS, mirpb.MIR_KEYWORDS, mirpb.MIR_CONTEXT],
            as_dict=True)

        test_utils.convert_dict_str_keys_to_int(mk)
        test_utils.convert_dict_str_keys_to_int(mc)

        self.assertEqual(mm['attributes'].keys(), expected_dict['mir_metadatas']['attributes'].keys())
        self.assertEqual(ma, expected_dict['mir_annotations'])
        self.assertEqual(mk, expected_dict['mir_keywords'])
        self.assertEqual(mc, expected_dict['mir_context'])

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
        self._data_img_path = os.path.join(self._data_root, 'images')
        os.makedirs(self._data_img_path)
        self._data_xml_path = os.path.join(self._data_root, 'gt')
        os.makedirs(self._data_xml_path)

        self._prepare_data()

    def _prepare_data(self):
        local_data_root = 'tests/assets'

        # Copy img files.
        img_files = ['2007_000032.jpg', '2007_000243.jpg']
        with open(self._idx_file, 'w') as idx_f:
            for file in img_files:
                src = os.path.join(local_data_root, file)
                dst = os.path.join(self._data_img_path, file)
                shutil.copyfile(src, dst)

                idx_f.writelines(dst + '\n')

        # Copy xml files.
        filenames = ['2007_000032.xml', '2007_000243.xml', 'pred_meta.yaml', 'coco-annotations.json']
        for file in filenames:
            src = os.path.join(local_data_root, file)
            dst = os.path.join(self._data_xml_path, file)
            shutil.copyfile(src, dst)

        # prepare zip file: {images: '2007_000032.xml', '2007_000243.xml', gt: ['coco-annotations.json']}
        with zipfile.ZipFile(os.path.join(self._data_root, 'dataset.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(os.path.join(self._data_img_path, '2007_000032.jpg'), 'dataset/images/2007_000032.jpg')
            zipf.write(os.path.join(self._data_img_path, '2007_000243.jpg'), 'dataset/images/2007_000243.jpg')
            zipf.write(os.path.join(self._data_xml_path, 'coco-annotations.json'), 'dataset/gt/coco-annotations.json')

    def _prepare_mir_repo(self):
        # init repo
        test_utils.mir_repo_init(self._mir_repo_root)
        # prepare branch a
        test_utils.mir_repo_create_branch(self._mir_repo_root, 'a')
