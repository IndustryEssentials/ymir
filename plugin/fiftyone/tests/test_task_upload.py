import os
from pathlib import Path

import fiftyone as fo

from app.worker import build_detections, build_sample


def test_build_detections():
    objects = [
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
    res = build_detections(objects, "ymir_data233", 1080, 1080)
    item = fo.Detection(
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

    sample = build_sample(base_path, img_path, annotation_path, "ymir_data233")

    assert sample["ground_truth"].detections[0].label == "人"
    assert sample["ground_truth"].detections[0].bounding_box == [
        0.08981481481481482,
        0.004629629629629629,
        0.6814814814814815,
        0.5333333333333333,
    ]
    assert sample["ground_truth"].detections[0].tags == [
        "ymir_data233",
    ]
