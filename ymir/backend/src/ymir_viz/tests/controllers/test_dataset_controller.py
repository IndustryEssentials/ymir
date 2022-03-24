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
            "ignored_labels": {
                'cat': 5,
            },
            "negative_info": {
                "negative_images_cnt": 0,
                "project_negative_images_cnt": 0,
            },
            "total_images_cnt": 1,
        }

        mocker.patch.object(MirStorageOps, "load_single_dataset", return_value=mir_dataset_content)
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/datasets")

        print(f"resp.data: {resp.data.decode('utf-8')}")
        assert resp.status_code == 200
        assert resp.json()["result"] == {
            'class_ids_count': {
                '3': 34
            },
            'ignored_labels': {
                'cat': 5
            },
            'negative_info': {
                'negative_images_cnt': 0,
                'project_negative_images_cnt': 0
            },
            'total_images_cnt': 1
        }
