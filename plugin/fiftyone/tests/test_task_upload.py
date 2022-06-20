import os
from pathlib import Path

from fiftyone import Sample, Polyline

from app.worker import (
    _build_polylines,
    _get_annotation,
    _add_detections,
    _set_metadata,
    _get_samples
)


def test_get_samples():
    base_path = Path(os.getcwd())
    annotation_dir = "tests/test_data/voc"

    data_name = "pd_ymir_dataset001"
    sample_pool = {}
    _get_samples(base_path, Path(annotation_dir), data_name, sample_pool)
    assert (
        sample_pool["241294009_432213948218468_252149922899382953_n.jpg"][data_name]
        .polylines[0]
        .label
        == "人"
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
    assert sample[dataset_type].polylines[0].points == [[(0.09034165571616294, 0.0049277266754270636),
                                                         (0.7720105124835743, 0.0049277266754270636),
                                                         (0.7720105124835743, 0.5387647831800263),
                                                         (0.09034165571616294, 0.5387647831800263)]]


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

    res = _build_polylines(voc_objects, 1080, 1080)
    polyline = Polyline(
        label="人",
        points=[[(0.3575148463553896, 0.2536834726595991),
                (0.13540946725882494, 0.33379375518621823),
                (0.06378144994090668, 0.1352054162292898),
                (0.28588682903747137, 0.05509513370267066)]],
        closed=True
    )
    polyline.tags = [
        "ymir_data233",
    ]
    polylines = [polyline]

    assert res[0].points == polylines[0].points
    assert res[0].label == polylines[0].label
