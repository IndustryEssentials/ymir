from typing import Any

from google.protobuf import json_format
from pytest_mock import plugin

from mir.tools import det_eval_ops
from mir.protos import mir_command_pb2 as mirpb


class TestEvaluationController:
    def test_dataset_fast_evaluate(self, test_client: Any, mocker: plugin.MockerFixture) -> None:
        user_id = "fake_user_id"
        repo_id = "fake_repo_id"
        branch_id = "fake_branch_id"

        evaluation_json = {
            'config': {
                'gt_dataset_id': 'a',
                'pred_dataset_ids': ['a'],
                'conf_thr': 0.3,
                'iou_thrs_interval': '0.5',
                'need_pr_curve': False
            },
            'dataset_evaluations': {
                'a': {
                    'conf_thr': 0.3,
                    'gt_dataset_id': 'a',
                    'pred_dataset_id': 'a',
                    'iou_evaluations': {
                        '0.50': {
                            'ci_evaluations': {
                                '2': {
                                    'ap': 1.0,
                                    'ar': 1.0,
                                    'tp': 2,
                                    'fp': 0,
                                    'fn': 0,
                                    'pr_curve': []
                                },
                                '0': {
                                    'ap': 1.0,
                                    'ar': 1.0,
                                    'tp': 2,
                                    'fp': 0,
                                    'fn': 0,
                                    'pr_curve': []
                                },
                                '1': {
                                    'ap': 1.0,
                                    'ar': 1.0,
                                    'tp': 1,
                                    'fp': 0,
                                    'fn': 0,
                                    'pr_curve': []
                                }
                            },
                            'ci_averaged_evaluation': {
                                'ap': 1.0,
                                'ar': 1.0,
                                'tp': 5,
                                'fp': 0,
                                'fn': 0,
                                'pr_curve': []
                            },
                            'ck_evaluations': {}
                        }
                    },
                    'iou_averaged_evaluation': {
                        'ci_evaluations': {
                            '2': {
                                'ap': 1.0,
                                'ar': 1.0,
                                'tp': 2,
                                'fp': 0,
                                'fn': 0,
                                'pr_curve': []
                            },
                            '0': {
                                'ap': 1.0,
                                'ar': 1.0,
                                'tp': 2,
                                'fp': 0,
                                'fn': 0,
                                'pr_curve': []
                            },
                            '1': {
                                'ap': 1.0,
                                'ar': 1.0,
                                'tp': 1,
                                'fp': 0,
                                'fn': 0,
                                'pr_curve': []
                            }
                        },
                        'ci_averaged_evaluation': {
                            'ap': 1.0,
                            'ar': 1.0,
                            'tp': 5,
                            'fp': 0,
                            'fn': 0,
                            'pr_curve': [{
                                'x': 0,
                                'y': 1,
                                'z': 0.5
                            }, {
                                'x': 1,
                                'y': 0,
                                'z': 0.2
                            }]
                        },
                        'ck_evaluations': {
                            'weather': {
                                'total': {
                                    'ap': 1.0,
                                    'ar': 1.0,
                                    'tp': 5,
                                    'fp': 0,
                                    'fn': 0,
                                    'pr_curve': []
                                },
                                'sub': {
                                    'sunny': {
                                        'ap': 1.0,
                                        'ar': 1.0,
                                        'tp': 5,
                                        'fp': 0,
                                        'fn': 0,
                                        'pr_curve': []
                                    }
                                }
                            },
                            'color': {
                                'total': {
                                    'ap': 1.0,
                                    'ar': 1.0,
                                    'tp': 5,
                                    'fp': 0,
                                    'fn': 0,
                                    'pr_curve': []
                                },
                                'sub': {
                                    'red': {
                                        'ap': 1.0,
                                        'ar': 1.0,
                                        'tp': 4,
                                        'fp': 0,
                                        'fn': 0,
                                        'pr_curve': []
                                    },
                                    'blue': {
                                        'ap': 0.33333334,
                                        'ar': 0.33333334,
                                        'tp': 1,
                                        'fp': 0,
                                        'fn': 0,
                                        'pr_curve': []
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        evaluation = mirpb.Evaluation()
        json_format.ParseDict(evaluation_json, evaluation)
        mocker.patch.object(det_eval_ops, 'det_evaluate_datasets', return_value=(evaluation, None))
        resp = test_client.get(
            f"/v1/users/{user_id}/repositories/{repo_id}/branches/{branch_id}/dataset_fast_evaluation"
            "?conf_thr=0.3&iou_thr=0.5&need_pr_curve=false")

        assert resp.status_code == 200
        assert resp.json()['result'] == evaluation_json['dataset_evaluations']
