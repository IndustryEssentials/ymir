import os
from pathlib import Path

from fiftyone import Sample, Detection

from app.worker import (
    _build_detections,
    _get_annotation,
    _add_detections,
    _set_metadata,
)


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
    res = _build_detections(objects, 1080, 1080)
    item = Detection(
        label="人",
        bounding_box=[
            0.08981481481481482,
            0.004629629629629629,
            0.6814814814814815,
            0.5333333333333333,
        ],
    )

    assert res[0].bounding_box == [item][0].bounding_box
    assert res[0].label == [item][0].label


def test_get_annotation():
    base_path = Path(os.getcwd())
    annotation_path = (
        "tests/test_data/voc/labels/241294009_432213948218468_252149922899382953_n.xml"
    )
    annotation = _get_annotation(base_path, annotation_path)
    assert annotation["object"]["name"] == "人"


def test_set_metadata():
    base_path = Path(os.getcwd())
    annotation_path = (
        "tests/test_data/voc/labels/241294009_432213948218468_252149922899382953_n.xml"
    )
    annotation = _get_annotation(base_path, annotation_path)
    sample = Sample(filepath=base_path / annotation_path)
    sample = _set_metadata(annotation, sample)
    assert sample["metadata"].width == 1080
    assert sample["metadata"].height == 1080
    assert sample["metadata"].num_channels == 3


def test_add_detections():
    base_path = Path(os.getcwd())
    dataset_type = "ground_truth"

    img_path = (
        "tests/test_data/voc/data/241294009_432213948218468_252149922899382953_n.jpg"
    )
    annotation_path = (
        "tests/test_data/voc/labels/241294009_432213948218468_252149922899382953_n.xml"
    )
    sample = Sample(filepath=base_path / img_path)
    annotation = _get_annotation(base_path, annotation_path)
    sample = _set_metadata(annotation, sample)
    sample = _add_detections(annotation, dataset_type, sample)

    assert sample[dataset_type].detections[0].label == "人"
    assert sample[dataset_type].detections[0].bounding_box == [
        0.08981481481481482,
        0.004629629629629629,
        0.6814814814814815,
        0.5333333333333333,
    ]
