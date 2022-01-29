from mir.tools.mir_storage_ops import MirStorageOps


class TestModelController:
    def test_get_model_info(self, test_client, mocker):
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "5928508c-1bc0-43dc-a094-0352079e39b5"

        mir_tasks_content = {"model_hash": "model_hash", "mean_average_precision": 0.88}

        mocker.patch.object(MirStorageOps, "load_single_model", return_value=mir_tasks_content)
        resp = test_client.get(f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/models")

        assert resp.status_code == 200
        assert resp.json()["result"] == {"model_id": "model_hash", "model_mAP": 0.88}
