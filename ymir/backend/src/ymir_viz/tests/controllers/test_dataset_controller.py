from mir.tools.mir_storage_ops import MirStorageOps


class TestDatasetController:
    def test_get_dataset_info(self, test_client, mocker):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"

        mir_dataset_content = {
            "class_ids_count": {
                3: 34
            },
            "negative_assets_count": 0,
            "total_assets_count": 1,
        }

        mocker.patch.object(MirStorageOps, "load_single_dataset", return_value=mir_dataset_content)
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/datasets")

        assert resp.status_code == 200
        assert resp.json()["result"] == {
            'class_ids_count': {
                '3': 34  # int is converted to str in json.dumps.
            },
            'negative_assets_count': 0,
            'total_assets_count': 1
        }

    def test_get_dataset_stats(self, test_client, mocker):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"

        mir_asset_contents = {
            "all_asset_ids": ["asset_id_0", "asset_id_1", "asset_id_2"],
            "asset_ids_detail": {
                "asset_id_0": {
                    "metadata": {
                        "asset_type": 2,
                        "width": 1080,
                        "height": 1620
                    },
                    "pred": [{
                        "box": {
                            "x": 26,
                            "y": 189,
                            "w": 19,
                            "h": 50
                        },
                        "class_id": 2,
                        "cm": 1,
                    }],
                    "gt": [{
                        "box": {
                            "x": 26,
                            "y": 189,
                            "w": 19,
                            "h": 50
                        },
                        "class_id": 2,
                        "cm": 1,
                    }],
                    "class_ids": [2],
                    "pred_class_ids": [2],
                    "gt_class_ids": [2],
                }
            },
            "class_ids_index": {
                1: ["asset_id_0", "asset_id_1", "asset_id_2"],
                2: ["asset_id_1"],
            },
            "pred_class_ids_index": {
                1: ["asset_id_0", "asset_id_1"],
            },
            "gt_class_ids_index": {
                1: ["asset_id_0", "asset_id_1", "asset_id_2"],
                2: ["asset_id_1"],
            }
        }

        mocker.patch.object(MirStorageOps, "load_assets_content", return_value=mir_asset_contents)
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/dataset_stats?class_ids=2")
        assert resp.status_code == 200
        assert resp.json()["result"] == {
            'total_assets_count': 3,
            'pred': {
                'class_ids_count': {
                    '2': 0,  # int is converted to str in json.dumps.
                },
                'negative_assets_count': 3,
            },
            'gt': {
                'class_ids_count': {
                    '2': 1,  # int is converted to str in json.dumps.
                },
                'negative_assets_count': 2,
            },
        }
