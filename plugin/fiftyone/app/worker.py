import csv
import math
from pathlib import Path
from typing import List, Dict, Tuple

import xmltodict
from celery import current_app as current_celery_app
from celery import shared_task
from fiftyone import Detection, Dataset, Sample, Polyline, Polylines
from fiftyone.core.metadata import ImageMetadata
from fiftyone.utils.voc import VOCBoundingBox

from app.models.schemas import Task
from conf.configs import conf


def create_celery() -> current_celery_app:
    """
    Create a celery app
    run: celery -A app.main.celery worker --loglevel=INFO
    """
    celery_app = current_celery_app
    celery_app.conf.broker_url = (
        f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
    )
    celery_app.conf.result_backend = (
        conf.mongo_uri
    )

    celery_app.conf.task_serializer = "pickle"
    celery_app.conf.result_serializer = "pickle"
    celery_app.conf.event_serializer = "json"
    celery_app.conf.accept_content = [
        "application/json",
        "application/x-python-serialize",
    ]
    celery_app.conf.result_accept_content = [
        "application/json",
        "application/x-python-serialize",
    ]

    return celery_app


@shared_task(name="load_task_data")
def load_task_data(task: Task) -> None:
    """
    :type task: Task
    """
    base_path = Path(conf.base_path)
    samples: List[Sample] = []
    for d in task.datas:
        data_dir = base_path / Path(d.data_dir)
        tsv_file = data_dir / "img.tsv"
        with tsv_file.open() as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            samples.extend(
                _build_sample(base_path, row[0], row[1], d.name) for row in rd
            )
    # Create dataset
    dataset = Dataset(task.tid)
    dataset.add_samples(samples)
    dataset.persistent = True


def _build_sample(
    base_path: Path, img_path: str, annotation_path: str, ymir_data_name: str
) -> Sample:
    annotation_file = base_path / annotation_path
    with annotation_file.open("r", encoding="utf-8") as ad:
        annotation = xmltodict.parse(ad.read()).get("annotation")
    size = annotation["size"]
    width = int(size["width"])
    height = int(size["height"])
    depth = int(size["depth"])
    metadata = ImageMetadata(
        width=width,
        height=height,
        num_channels=depth,
    )

    voc_objects = []
    if isinstance(annotation["object"], dict):
        voc_objects.append(annotation["object"])
    elif isinstance(annotation["object"], list):
        voc_objects = annotation["object"]
    else:
        raise ValueError(f"Invalid object type: {type(annotation['object'])}")

    sample = Sample(filepath=base_path / img_path)
    polylines = _build_polylines(voc_objects, ymir_data_name, width, height)
    sample["ground_truth"] = Polylines(polylines=polylines)
    sample["metadata"] = metadata
    return sample


def _build_detections(
    voc_objects: list, ymir_data_name: str, width: int, height: int
) -> List[Detection]:
    detections = []
    for obj in voc_objects:
        label = obj["name"]
        bndbox = VOCBoundingBox.from_bndbox_dict(obj["bndbox"]).to_detection_format(
            frame_size=(width, height)
        )
        item = Detection(
            label=label,
            bounding_box=bndbox,
        )
        item.tags = [
            ymir_data_name,
        ]
        detections.append(item)
    return detections


def _build_polylines(
    voc_objects: list, ymir_data_name: str, width: int, height: int
) -> List[Polyline]:
    polylines = []
    for obj in voc_objects:
        label = obj["name"]
        points = _get_points_from_bndbox(obj["bndbox"])
        points = [(point[0] / width, point[1] / height) for point in points]
        polyline = Polyline(
            label=label,
            points=[points],
            closed=True
        )
        polyline.tags = [
            ymir_data_name,
        ]
        polylines.append(polyline)
    return polylines


def _get_points_from_bndbox(bndbox: Dict) -> list:
    xmin, ymin = int(float(bndbox.get("xmin", 0))), int(float(bndbox.get("ymin", 0)))
    xmax, ymax = int(float(bndbox.get("xmax", 0))), int(float(bndbox.get("ymax", 0)))
    angle = float(bndbox.get("rotate_angle", 0))

    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    w, h = xmax - xmin, ymax - ymin

    p0x, p0y = _rotate_point(cx, cy, cx - w / 2, cy - h / 2, -angle)
    p1x, p1y = _rotate_point(cx, cy, cx + w / 2, cy - h / 2, -angle)
    p2x, p2y = _rotate_point(cx, cy, cx + w / 2, cy + h / 2, -angle)
    p3x, p3y = _rotate_point(cx, cy, cx - w / 2, cy + h / 2, -angle)

    points = [(p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)]

    return points


def _rotate_point(xc: float, yc: float, xp: float, yp: float, theta: float) -> Tuple[int, int]:
    xoff = xp-xc
    yoff = yp-yc

    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    resx = cos_theta * xoff + sin_theta * yoff
    resy = - sin_theta * xoff + cos_theta * yoff

    return int(xc + resx), int(yc + resy)