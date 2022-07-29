import pytest
from mir.tools.mir_storage_ops import MirStorageOps


@pytest.fixture()
def mock_mir_content(mocker):
    mocker.patch.object(
        MirStorageOps,
        "load_assets_content",
        return_value={
            "all_asset_ids": ["asset_id"],
            "asset_ids_detail": {
                "asset_id": {
                    "metadata": {"asset_type": 2, "width": 1080, "height": 1620},
                    "pred": [
                        {
                            "box": {"x": 26, "y": 189, "w": 19, "h": 50},
                            "class_id": 2,
                            "cm": 1,
                        }
                    ],
                    "gt": [
                        {
                            "box": {"x": 26, "y": 189, "w": 19, "h": 50},
                            "class_id": 2,
                            "cm": 1,
                        }
                    ],
                    "class_ids": [2],
                }
            },
            "class_ids_index": {
                2: ["asset_id"],
            },
        },
    )


class TestAssetController:
    def test_get_assets_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets")
        assert resp.status_code == 200
        res = resp.json()["result"]["elements"][0]
        assert "gt" in res
        assert "pred" in res

        filter_class_id = "class_id=2"
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets?{filter_class_id}"
        )
        assert resp.status_code == 200
        res = resp.json()["result"]["elements"][0]
        assert "gt" in res
        assert "pred" in res

    def atest_get_asset_id_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"
        asset_id = "asset_id"

        expect_data = {
            "asset_id": asset_id,
            "pred": [{"box": {"h": 50, "w": 19, "x": 26, "y": 189}, "class_id": 2, "cm": 1}],
            "gt": [{"box": {"h": 50, "w": 19, "x": 26, "y": 189}, "class_id": 2, "cm": 1}],
            "class_ids": [2],
            "metadata": {"asset_type": 2, "height": 1620, "width": 1080},
        }
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets/{asset_id}")

        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data
