import pytest
from mir.tools.mir_storage_ops import MirStorageOps


@pytest.fixture()
def mock_mir_content(mocker):
    mocker.patch.object(MirStorageOps,
                        "load_assets_content",
                        return_value={
                            "all_asset_ids": ["asset_id"],
                            "asset_ids_detail": {
                                "asset_id": {
                                    "metadata": {
                                        "asset_type": 2,
                                        "width": 1080,
                                        "height": 1620
                                    },
                                    "annotations": [{
                                        "box": {
                                            "x": 26,
                                            "y": 189,
                                            "w": 19,
                                            "h": 50
                                        },
                                        "class_id": 2
                                    }],
                                    "class_ids": [2],
                                }
                            },
                            "class_ids_index": {
                                2: ["asset_id"],
                            },
                        })


class TestAssetController:
    def test_get_asserts_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"
        expect_data = {"elements": [{"asset_id": "asset_id", "class_ids": [2]}], "limit": 20, "offset": 0, 'total': 1}
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets")
        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data

        expect_data = {'elements': [{'asset_id': 'asset_id', 'class_ids': [2]}], 'limit': 20, 'offset': 0, 'total': 1}
        filter_class_id = "class_id=2"
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets?{filter_class_id}")
        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data

    def test_get_assert_id_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"
        asset_id = "asset_id"

        expect_data = {
            'annotations': [{
                'box': {
                    'h': 50,
                    'w': 19,
                    'x': 26,
                    'y': 189
                },
                'class_id': 2
            }],
            'class_ids': [2],
            'metadata': {
                'asset_type': 2,
                'height': 1620,
                'width': 1080
            }
        }
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets/{asset_id}")

        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data
