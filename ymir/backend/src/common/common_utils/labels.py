from collections import Counter
import logging
import os
import time
from typing import Any, Dict, Iterable, List, Set

from pydantic import BaseModel, validator
import yaml


EXPECTED_FILE_VERSION = 1


class SingleLabel(BaseModel):
    id: int
    name: str
    create_time: float = 0
    update_time: float = 0
    aliases: List[str] = []

    @validator('name')
    def _strip_and_lower_name(cls, v: str) -> str:
        return v.strip().lower()

    @validator('aliases', each_item=True)
    def _strip_and_lower_alias(cls, v: str) -> str:
        return v.strip().lower()


class LabelStorage(BaseModel):
    version: int = EXPECTED_FILE_VERSION
    labels: List[SingleLabel] = []

    @validator('version')
    def _check_version(cls, v: int) -> int:
        if v != EXPECTED_FILE_VERSION:
            raise ValueError(f"incorrect version: {v}, needed {EXPECTED_FILE_VERSION}")
        return v

    @validator('labels')
    def _check_labels(cls, labels: List[SingleLabel]) -> List[SingleLabel]:
        label_names_set: Set[str] = set()
        for idx, label in enumerate(labels):
            if label.id != idx:
                raise ValueError(f"invalid label id: {label.id}, expected {idx}")

            # all label names and aliases should have no dumplicate
            name_and_aliases = label.aliases + [label.name]
            name_and_aliases_set = set(name_and_aliases)
            if len(name_and_aliases) != len(name_and_aliases_set):
                raise ValueError(f"duplicated inline label: {name_and_aliases}")
            duplicated = set.intersection(name_and_aliases_set, label_names_set)
            if duplicated:
                raise ValueError(f"duplicated: {duplicated}")
            label_names_set.update(name_and_aliases_set)
        return labels


class UserLabels(LabelStorage):
    id_to_name: Dict[int, str] = {}
    name_to_id: Dict[str, int] = {}

    def __init__(self, **data: Any):
        super().__init__(**data)
        for label in self.labels:
            self.id_to_name[label.id] = label.name
            self.name_to_id[label.name] = label.id

    class Config:
        fields = {'labels': {'include': True}}

    def get_class_id(self, keyword: str):
        return self.name_to_id[keyword]

    def get_class_ids(self, keywords: List[str]):
        return [self.name_to_id[keyword] for keyword in keywords]

    def get_keyword(self, class_id: int):
        return self.id_to_name[class_id]

    def get_keywords(self, class_ids: List[int]):
        return [self.id_to_name[class_id] for class_id in class_ids]


def labels_file_name() -> str:
    return 'labels.yaml'


def labels_file_path(label_file_dir: str) -> str:
    os.makedirs(label_file_dir, exist_ok=True)
    return os.path.join(label_file_dir, labels_file_name())


def _write_label_file(label_file_dir: str, all_labels: List[SingleLabel]) -> None:
    """
    dump all label content into a label storage file, old file contents will be lost
    Args:
        all_labels (List[SingleLabel]): all labels
    """
    label_storage = LabelStorage(labels=all_labels)
    with open(labels_file_path(label_file_dir), 'w') as f:
        yaml.safe_dump(label_storage.dict(), f)


def get_all_labels(label_file_dir: str) -> LabelStorage:
    """
    get all labels from label storage file

    Returns:
    List[SingleLabel]: all labels

    Raises:
        FileNotFoundError: if label storage file not found
        ValueError: if version mismatch
        Error: if parse failed or other error occured
    """
    with open(labels_file_path(label_file_dir), 'r') as f:
        obj = yaml.safe_load(f)
    if obj is None:
        obj = {}

    label_storage = LabelStorage(**obj)

    return label_storage


def merge_labels(label_file_dir: str, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
    # TODO: too hard to read, make it simpler in another pr

    # check `candidate_labels` has no duplicate
    candidate_labels_list = [x.strip().lower().split(",") for x in candidate_labels]
    candidates_list = [x for row in candidate_labels_list for x in row]
    if len(candidates_list) != len(set(candidates_list)):
        logging.error(f"conflict labels: {candidate_labels_list}")
        return candidate_labels_list

    current_timestamp = time.time()

    # all labels in storage file
    existed_labels = get_all_labels(label_file_dir=label_file_dir).labels
    # key: label name, value: idx
    existed_main_names_to_ids: Dict[str, int] = {label.name: idx for idx, label in enumerate(existed_labels)}

    # for main names in `existed_main_names_to_ids`, update alias
    # for new main names, add them to `candidate_labels_list_new`
    candidate_labels_list_new: List[List[str]] = []
    for candidate_list in candidate_labels_list:
        main_name = candidate_list[0]
        if main_name in existed_main_names_to_ids:  # update alias
            idx = existed_main_names_to_ids[main_name]
            # update `existed_labels`
            label = existed_labels[idx]
            label.name = candidate_list[0]
            label.aliases = candidate_list[1:]
            label.update_time = current_timestamp
        else:  # new main_names
            candidate_labels_list_new.append(candidate_list)

    # check dumplicate for `existed_labels_list`
    existed_labels_list = []
    for label in existed_labels:
        existed_labels_list.append(label.name)
        existed_labels_list.extend(label.aliases)
    existed_labels_dups = set([k for k, v in Counter(existed_labels_list).items() if v > 1])
    if existed_labels_dups:
        conflict_labels = []
        for candidate_list in candidate_labels_list:
            if set.intersection(set(candidate_list), existed_labels_dups):  # at least one label exist.
                conflict_labels.append(candidate_list)
        logging.error(f"conflict labels: {conflict_labels}")
        return conflict_labels

    existed_labels_set = set(existed_labels_list)

    # insert new main_names.
    conflict_labels = []
    for candidate_list in candidate_labels_list_new:
        candidate_set = set(candidate_list)
        if set.intersection(candidate_set, existed_labels_set):  # at least one label exist.
            conflict_labels.append(candidate_list)
            continue

        existed_labels.append(
            SingleLabel(id=len(existed_labels),
                        name=candidate_list[0],
                        aliases=candidate_list[1:],
                        create_time=current_timestamp,
                        update_time=current_timestamp))
        existed_labels_set.update(candidate_set)

    if not (check_only or conflict_labels):
        _write_label_file(label_file_dir, existed_labels)
    if conflict_labels:
        logging.error(f"conflict labels: {conflict_labels}")
    return conflict_labels


def get_main_labels_by_ids(label_file_dir: str, type_ids: Iterable) -> List[str]:
    all_labels = get_all_labels(label_file_dir=label_file_dir).labels
    return [all_labels[int(idx)].name for idx in type_ids]


def create_empty(label_file_dir: str) -> None:
    label_file = labels_file_path(label_file_dir)
    if os.path.isfile(label_file):
        raise FileExistsError(f"already exists: {label_file}")

    with open(label_file, 'w') as f:
        yaml.safe_dump(LabelStorage().dict(), f)
