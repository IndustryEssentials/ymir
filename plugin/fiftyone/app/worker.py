import csv
from pathlib import Path
from typing import List, Dict

import xmltodict
from celery import current_app as current_celery_app
from celery import shared_task
from fiftyone import Detection, Dataset, Sample, Detections
from fiftyone.core.metadata import ImageMetadata
from fiftyone.utils.voc import VOCBoundingBox

from app.models.schemas import Task
from conf.configs import conf
from utils.constants import DataSetResultTypes


def create_celery() -> current_celery_app:
    """
    Create a celery app
    run: celery -A app.main.celery worker --loglevel=INFO -P threads
    """
    celery_app = current_celery_app
    celery_app.conf.broker_url = (
        f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
    )
    celery_app.conf.result_backend = (
        f"redis://{conf.redis_host}:{conf.redis_port}/{conf.redis_db}"
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
    sample_pool: Dict[str, Sample] = {}
    for d in task.datas:
        data_dir = base_path / Path(d.data_dir)
        tsv_file = data_dir / "img.tsv"
        with tsv_file.open() as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')

            for row in rd:
                img_path: str = row[0]
                if img_path in sample_pool:
                    sample = sample_pool[img_path]
                else:
                    sample = Sample(filepath=base_path / img_path)
                    sample_pool[img_path] = sample
                if d.data_type == DataSetResultTypes.GROUND_TRUTH:
                    _build_sample(base_path, row[1], d.data_type, sample)
                else:
                    _build_sample(base_path, row[1], d.name, sample)

    # Create dataset
    dataset = Dataset(task.tid)
    dataset.add_samples(sample_pool.values())
    dataset.persistent = True


def _build_sample(
    base_path: Path,
    annotation_path: str,
    ymir_data_name: str,
    sample: Sample,
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
    detections = _build_detections(voc_objects, width, height)

    sample[ymir_data_name] = Detections(detections=detections)
    sample["metadata"] = metadata
    return sample


def _build_detections(voc_objects: list, width: int, height: int) -> List[Detection]:
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
        detections.append(item)
    return detections
