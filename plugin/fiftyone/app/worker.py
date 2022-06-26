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
    run: celery -A app.main.celery worker --loglevel=INFO -P threads
    """
    celery_app = current_celery_app
    celery_app.conf.broker_url = (
        f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
    )
    celery_app.conf.result_backend = f"{conf.mongo_uri}/{conf.fiftyone_database_name}"

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
    load task data
    :type task: Task
    return: None
    """
    base_path = Path(conf.base_path)
    sample_pool: Dict[str, Sample] = {}
    for d in task.datas:
        prd_data_dir = base_path / Path(d.data_dir) / "annotations"
        gt_data_dir = base_path / Path(d.data_dir) / "groundtruth"
        _get_samples(base_path, prd_data_dir, f"pd_{d.name}", sample_pool)
        _get_samples(base_path, gt_data_dir, f"gt_{d.name}", sample_pool)

    # Create dataset
    dataset = Dataset(task.tid)
    dataset.add_samples(sample_pool.values())
    dataset.persistent = True


def _get_samples(base_path: Path, labels_dir: Path, dataset_name, sample_pool,) -> None:
    """
    get annotation from voc xml file
    :type base_path: Path
    return: dict
    """
    tsv_file = labels_dir / "index.tsv"
    with tsv_file.open() as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')

        for row in rd:
            img_path = labels_dir.parent / "images" / Path(row[0])
            annotation = _get_annotation(labels_dir, row[1])

            if img_path.name in sample_pool:
                sample = sample_pool[img_path.name]
            else:
                sample = Sample(filepath=img_path)
                if annotation.get("cks"):
                    for k, v in annotation.get("cks", {}).items():
                        sample[k] = v
                sample_pool[img_path.name] = sample
                _set_metadata(annotation, sample)
            # if object is empty, skip
            if "object" not in annotation:
                continue

            _add_detections(annotation, dataset_name, sample)


def _get_annotation(
    base_path: Path,
    annotation_path: str,
) -> dict:
    """
    get annotation from voc xml file
    :type base_path: Path
    :type annotation_path: str
    return: dict
    """
    annotation_file = base_path / annotation_path
    with annotation_file.open("r", encoding="utf-8") as ad:
        return xmltodict.parse(ad.read()).get("annotation")


def _set_metadata(
    annotation: dict,
    sample: Sample,
) -> Sample:
    """
    set metadata to sample
    :type annotation: dict
    :type sample: Sample
    return: sample
    """
    size = annotation["size"]
    width = int(size["width"])
    height = int(size["height"])
    depth = int(size["depth"])
    metadata = ImageMetadata(
        width=width,
        height=height,
        num_channels=depth,
    )
    sample["metadata"] = metadata
    return sample


def _add_detections(
    annotation: dict,
    ymir_data_name: str,
    sample: Sample,
) -> Sample:
    """
    add detections to sample
    :type annotation: dict
    :type ymir_data_name: str
    :type sample: Sample
    return: sample
    """
    voc_objects = []
    if isinstance(annotation["object"], dict):
        voc_objects.append(annotation["object"])
    elif isinstance(annotation["object"], list):
        voc_objects = annotation["object"]
    else:
        raise ValueError(f"Invalid object type: {type(annotation['object'])}")

    polylines = _build_polylines(voc_objects, sample["metadata"]["width"], sample["metadata"]["height"])
    sample[ymir_data_name] = Polylines(polylines=polylines)
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
            closed=True
        )
        if obj.get("tags"):
            for k, v in obj.get("tags").items():
                polyline[k] = v
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
