import pytest

from proto import backend_pb2
from mir.tools.mir_storage_ops import MirStorageOps


@pytest.fixture()
def mock_mir_content(mocker):
    dict_keywords = {
        "keywords": {
            "d4e4a60147f1e35bc7f5bc89284aa16073b043c9": {
                "predifined_keyids": [52]
            },
            "430df22960b0f369318705800139fcc8ec38a3e4": {
                "predifined_keyids": [2, 52]
            },
        },
        "predifined_keyids_cnt": {
            52: 2,
            2: 1
        },
        "predifined_keyids_total": 3,
        "index_predifined_keyids": {
            2: {
                "asset_ids": ["430df22960b0f369318705800139fcc8ec38a3e4"]
            },
            52: {
                "asset_ids": ["430df22960b0f369318705800139fcc8ec38a3e4", "d4e4a60147f1e35bc7f5bc89284aa16073b043c9"]
            },
        },
    }

    dict_annotations = {
        "task_annotations": {
            "5928508c-1bc0-43dc-a094-0352079e39b5": {
                "image_annotations": {
                    "d4e4a60147f1e35bc7f5bc89284aa16073b043c9": {
                        "annotations": [{
                            "box": {
                                "x": 26,
                                "y": 189,
                                "w": 19,
                                "h": 50
                            },
                            "class_id": 2
                        }]
                    }
                }
            }
        },
        "head_task_id": "5928508c-1bc0-43dc-a094-0352079e39b5",
    }

    dict_metadatas = {
        "attributes": {
            "d4e4a60147f1e35bc7f5bc89284aa16073b043c9": {
                "asset_type": "2",
                "width": 1080,
                "height": 1620,
                "image_channels": 3,
            },
            "430df22960b0f369318705800139fcc8ec38a3e4": {
                "asset_type": "2",
                "width": 1080,
                "height": 1620,
                "image_channels": 3,
            },
        }
    }

    mocker.patch.object(
        MirStorageOps,
        "load",
        return_value={
            backend_pb2.MirStorage.MIR_METADATAS: dict_metadatas,
            backend_pb2.MirStorage.MIR_ANNOTATIONS: dict_annotations,
            backend_pb2.MirStorage.MIR_KEYWORDS: dict_keywords,
        },
    )


class TestAssetController:
    def test_get_asserts_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "5928508c-1bc0-43dc-a094-0352079e39b5"
        expect_data = {
            "class_ids_count": {
                "2": 1,
                "52": 2
            },
            "elements": [
                {
                    "asset_id": "d4e4a60147f1e35bc7f5bc89284aa16073b043c9",
                    "class_ids": [52]
                },
                {
                    "asset_id": "430df22960b0f369318705800139fcc8ec38a3e4",
                    "class_ids": [2, 52]
                },
            ],
            "limit":
            20,
            "offset":
            0,
            "total":
            2,
        }
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets")
        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data

        expect_data = {
            "class_ids_count": {
                "2": 1,
                "52": 2
            },
            "elements": [{
                "asset_id": "430df22960b0f369318705800139fcc8ec38a3e4",
                "class_ids": [2, 52]
            }],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }
        filter_class_id = "class_id=2"
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets?{filter_class_id}")
        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data

    def test_get_assert_id_info(self, test_client, mock_mir_content):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"
        asset_id = "d4e4a60147f1e35bc7f5bc89284aa16073b043c9"

        expect_data = {
            "metadata": {
                "asset_type": "2",
                "width": 1080,
                "height": 1620,
                "image_channels": 3
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
            "class_ids": [52],
        }
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets/{asset_id}")

        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data

        asset_id = "430df22960b0f369318705800139fcc8ec38a3e4"
        expect_data = {
            "annotations": [],
            "class_ids": [2, 52],
            "metadata": {
                "asset_type": "2",
                "height": 1620,
                "image_channels": 3,
                "width": 1080
            },
        }
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/assets/{asset_id}")

        assert resp.status_code == 200
        assert resp.json()["result"] == expect_data
