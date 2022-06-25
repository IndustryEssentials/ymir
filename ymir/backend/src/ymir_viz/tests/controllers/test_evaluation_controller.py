from typing import Any
from pytest_mock import plugin

from mir.tools import det_eval
from mir.protos import mir_command_pb2 as mirpb


class TestEvaluationController:
    def test_dataset_fast_evaluate(self, test_client: Any, mocker: plugin.MockerFixture) -> None:
        user_id = "fake_user_id"
        repo_id = "fake_repo_id"
        branch_id = "fake_branch_id"

        expected_evaluation_json = {'dataset_evaluations': {}}
        mocker.patch.object(det_eval, 'det_evaluate', return_value=mirpb.Evaluation())
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/dataset_fast_evaluation"
            "?conf_thr=0.0005&iou_thr=0.5")

        assert resp.status_code == 200
        assert resp.json()['result'] == expected_evaluation_json
