import csv
import os
from pathlib import Path

import fiftyone as fo  # type: ignore
import fiftyone.core.metadata as fom  # type: ignore
import xmltodict  # type: ignore
from celery import Celery  # type: ignore
from fiftyone.utils.voc import VOCBoundingBox  # type: ignore

from app.models.schemas import Task
from conf.configs import conf

celery = Celery(__name__)
celery.conf.broker_url = f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
celery.conf.result_backend = (
    f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
)

celery.conf.task_serializer = "pickle"
celery.conf.result_serializer = "pickle"
celery.conf.event_serializer = "json"
celery.conf.accept_content = ["application/json", "application/x-python-serialize"]
celery.conf.result_accept_content = [
    "application/json",
    "application/x-python-serialize",
]


@celery.task(name="load_task_data")
def load_task_data(task: Task):
    """
    :type task: Task
    """
    base_path = Path(conf.base_path)
    samples: list[fo.Sample] = []
    for d in task.datas:
        data_dir = base_path / Path(d.data_dir)
        tsv_file = data_dir / "img.tsv"
        with tsv_file.open() as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            samples.extend(
                build_sample(base_path, row[0], row[1], d.name) for row in rd
            )
    # Create dataset
    dataset = fo.Dataset(task.tid)
    dataset.add_samples(samples)
    dataset.persistent = True


def build_sample(
    base_path: Path, img_path: str, annotation_path: str, ymir_data_name: str
) -> fo.Sample:
    annotation_file = base_path / annotation_path
    with annotation_file.open("r", encoding="utf-8") as ad:
        annotation = xmltodict.parse(ad.read()).get("annotation")
    size = annotation["size"]
    width = int(size.get("width", 0))
    height = int(size.get("height", 0))
    depth = int(size.get("depth", 0))
    metadata = fom.ImageMetadata(
        width=width,
        height=height,
        num_channels=depth,
    )

    objects = []
    if isinstance(annotation["object"], dict):
        objects.append(annotation["object"])
    else:
        objects = annotation["object"]
    detections = build_detections(objects, annotation, width, height)

    sample = fo.Sample(filepath=base_path / img_path)
    sample["ground_truth"] = fo.Detections(detections=detections)
    sample["metadata"] = metadata
    return sample


def build_detections(
    objects: list, ymir_data_name: str, width: int, height: int
) -> list[fo.Detection]:
    detections = []
    for obj in objects:
        label = obj["name"]
        bndbox = VOCBoundingBox.from_bndbox_dict(obj["bndbox"]).to_detection_format(
            frame_size=(width, height)
        )
        item = fo.Detection(
            label=label,
            bounding_box=bndbox,
        )
        item.tags = [
            ymir_data_name,
        ]
        detections.append(item)
    return detections
