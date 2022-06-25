class TestEvaluationController:
    def test_dataset_fast_evaluate(self, test_client, mocker) -> None:
        user_id = "fake_user_id"
        repo_id = "fake_repo_id"
        branch_id = "fake_branch_id"

        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/dataset_fast_evaluation"
            "?conf_thr=0.0005&iou_thr=0.5")
        breakpoint()
        print('')
