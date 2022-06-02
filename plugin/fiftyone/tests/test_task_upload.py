import os
from pathlib import Path

from fiftyone import Sample, Polyline

from app.worker import (
    _build_polylines,
    _get_annotation,
    _add_detections,
    _set_metadata,
)


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

    assert sample[dataset_type].polylines[0].label == "人"
    assert sample[dataset_type].polylines[0].points == [[(0.08981481481481482, 0.004629629629629629),
                                                         (0.7712962962962963, 0.004629629629629629),
                                                         (0.7712962962962963, 0.537962962962963),
                                                         (0.08981481481481482, 0.537962962962963)]]


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
