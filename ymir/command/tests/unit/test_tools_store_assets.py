import os
import shutil
import unittest

import mir.tools.utils as mir_utils
from tests import utils as test_utils


class TestStoreAssetsToDir(unittest.TestCase):
    def test_00(self):
        asset_ids = ["997c3e6ebd3e59dbe32656099c461e417c4693a3", '917c3e6ebd3e59dbe32656099c4614417c4693a3']
        tmp_dir = test_utils.dir_test_root(self.id().split(".")[-3:])
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)

        src_folder = os.path.join(tmp_dir, 'img')
        os.makedirs(src_folder, exist_ok=True)
        for id in asset_ids:
            with open(os.path.join(src_folder, id), 'w') as f:
                f.write("1")

        asset_id_to_rel_paths = mir_utils.store_assets_to_dir(asset_ids=asset_ids,
                                                              out_root=tmp_dir,
                                                              sub_folder='media',
                                                              asset_location=src_folder)
        self.assertEqual(set(asset_ids), set(asset_id_to_rel_paths.keys()))
        for _, asset_path in asset_id_to_rel_paths.items():
            self.assertTrue(os.path.isfile(os.path.join(tmp_dir, asset_path)))
        shutil.rmtree(tmp_dir)
