from typing import Any
from random import randint
from app.libs import predictions as m


class TestEvaluatePrediction:
    def test_evaluate_predictions(self, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        confidence_threshold = 0.233
        iou = 0.5
        require_average_iou = True
        need_pr_curve = True
        ctrl = mocker.Mock(evaluate_prediction=mocker.Mock(return_value={}))
        user_labels = mocker.Mock()
        predictions_mapping = {"a": 1, "b": 2}
        m.evaluate_predictions(
            ctrl,
            user_id,
            project_id,
            user_labels,
            confidence_threshold,
            iou,
            require_average_iou,
            need_pr_curve,
            "main_ck",
            predictions_mapping,
        )

        ctrl.evaluate_prediction.assert_called()


class TestConvertIou:
    def test_convert_to_iou_thrs_interval(self, mocker: Any) -> None:
        assert m.convert_to_iou_thrs_interval(None, True) == "0.5:0.95:0.05"
        assert m.convert_to_iou_thrs_interval(0.1, True) == "0.1:0.95:0.05"
        assert m.convert_to_iou_thrs_interval(0.1, False) == "0.1"
        assert m.convert_to_iou_thrs_interval(None, False) is None
