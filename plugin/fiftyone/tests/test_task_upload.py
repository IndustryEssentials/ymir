import os
from pathlib import Path

from fiftyone import Detection, Polyline

from app.worker import _build_detections, _build_sample, _build_polylines


def test_build_detections():
    voc_objects = [
        {
            "name": "人",
            "pose": "Unspecified",
            "truncated": "0",
            "difficult": "0",
            "bndbox": {
                "xmin": "97.56898817345598",
                "ymin": "5.321944809461235",
                "xmax": "833.7713534822602",
                "ymax": "581.8659658344284",
            },
        }
    ]
    res = _build_detections(voc_objects, "ymir_data233", 1080, 1080)
    item = Detection(
        label="人",
        bounding_box=[
            0.08981481481481482,
            0.004629629629629629,
            0.6814814814814815,
            0.5333333333333333,
        ],
    )
    item.tags = [
        "ymir_data233",
    ]

    assert res[0].bounding_box == [item][0].bounding_box
    assert res[0].label == [item][0].label


def test_build_sample():
    base_path = Path(os.getcwd())

    img_path = (
        "tests/test_data/voc/data/241294009_432213948218468_252149922899382953_n.jpg"
    )
    annotation_path = (
        "tests/test_data/voc/labels/241294009_432213948218468_252149922899382953_n.xml"
    )

    sample = _build_sample(base_path, img_path, annotation_path, "ymir_data233")

    assert sample["ground_truth"].polylines[0].label == "人"
    assert sample["ground_truth"].polylines[0].points == [[(0.08981481481481482, 0.004629629629629629),
                                                           (0.7712962962962963, 0.004629629629629629),
                                                           (0.7712962962962963, 0.537962962962963),
                                                           (0.08981481481481482, 0.537962962962963),]]
    assert sample["ground_truth"].polylines[0].tags == [
        "ymir_data233",
    ]


def test_build_polylines():
    voc_objects = [
        {
            "name": "人",
            "pose": "Unspecified",
            "truncated": "0",
            "difficult": "0",
            "bndbox": {
                "xmin": "100",
                "ymin": "96",
                "xmax": "355",
                "ymax": "324",
                "rotate_angle": "2.889813"
            },
        }
    ]
    res = _build_polylines(voc_objects, "ymir_data233", 1080, 1080)
    polyline = Polyline(
        label="人",
        points=[[(0.3509259259259259, 0.26666666666666666),
                (0.12222222222222222, 0.32592592592592595),
                (0.06944444444444445, 0.12129629629629629),
                (0.29814814814814816, 0.062037037037037036)]],
        closed=True
    )
    polyline.tags = [
        "ymir_data233",
    ]
    polylines = [polyline]

    assert res[0].points == polylines[0].points
    assert res[0].label == polylines[0].label