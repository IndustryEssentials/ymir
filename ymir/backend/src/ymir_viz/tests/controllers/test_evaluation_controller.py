class TestEvaluationController:
    def test_dataset_fast_evaluate(self, test_client, mocker) -> None:
        user_id = "user_id"
        repo_id = "repo_id"
        branch_id = "branch_id"

        resp = test_client.get(f"/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/dataset_fast_evaluation")
        breakpoint()
        print('')
