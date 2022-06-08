import csv
import math
from pathlib import Path
from typing import List, Dict, Tuple

import xmltodict
from celery import current_app as current_celery_app
from celery import shared_task
from fiftyone import Dataset, Sample, Polyline, Polylines
from fiftyone.core.metadata import ImageMetadata

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
        conf.mongo_uri + "/" + conf.fiftyone_database_name
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
    polylines = _build_polylines(voc_objects, width, height)
    sample["ground_truth"] = Polylines(polylines=polylines)
    sample["metadata"] = metadata
    return sample


def _build_polylines(voc_objects: list, width: int, height: int) -> List[Polyline]:
    polylines = []
    for obj in voc_objects:
        label = obj["name"]
        points = _get_points_from_bndbox(obj["bndbox"], width, height)
        polyline = Polyline(
            label=label,
            points=[points],
            confidence=obj.get("confidence"),
            ck=obj.get("ck"),
            closed=True
        )
        polylines.append(polyline)
    return polylines


def _get_points_from_bndbox(bndbox: Dict, width: int, height: int) -> list:
    # raise error if parameter not exist
    xmin, ymin = float(bndbox["xmin"]), float(bndbox["ymin"])
    xmax, ymax = float(bndbox["xmax"]), float(bndbox["ymax"])
    angle = float(bndbox.get("rotate_angle", 0)) * math.pi

    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    half_w, half_h = (xmax - xmin) / 2, (ymax - ymin) / 2

    p0x, p0y = _rotate_point(cx, cy, cx - half_w, cy - half_h, -angle, width, height)
    p1x, p1y = _rotate_point(cx, cy, cx + half_w, cy - half_h, -angle, width, height)
    p2x, p2y = _rotate_point(cx, cy, cx + half_w, cy + half_h, -angle, width, height)
    p3x, p3y = _rotate_point(cx, cy, cx - half_w, cy + half_h, -angle, width, height)

    return [(p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)]


def _rotate_point(cx: float, cy: float, xp: float, yp: float, theta: float, width: int,
                  height: int) -> Tuple[float, float]:
    xoff = xp - cx
    yoff = yp - cy

    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    resx = cos_theta * xoff + sin_theta * yoff
    resy = - sin_theta * xoff + cos_theta * yoff

    return (cx + resx) / width, (cy + resy) / height
