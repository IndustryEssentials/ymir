from collections import Counter
from datetime import datetime
import logging
import os
from typing import Any, Dict, Iterator, List, Set

from google.protobuf import json_format
from pydantic import BaseModel, validator
import yaml

from proto import backend_pb2

EXPECTED_FILE_VERSION = 1


class SingleLabel(BaseModel):
    id: int = -1
    name: str
    create_time: datetime = datetime(year=2022, month=1, day=1)
    update_time: datetime = datetime(year=2022, month=1, day=1)
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
            if label.id < 0:
                label.id = idx
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
    name_aliases_to_id: Dict[str, int] = {}

    def __init__(self, **data: Any):
        super().__init__(**data)
        for label in self.labels:
            self.id_to_name[label.id] = label.name
            self.name_to_id[label.name] = label.id
            self.name_aliases_to_id[label.name] = label.id
            for alias in label.aliases:
                self.name_aliases_to_id[alias] = label.id

    class Config:
        fields = {'labels': {'include': True}}

    def get_class_id(self, name_or_aliaes: str):
        return self.name_aliases_to_id[name_or_aliaes]

    def get_class_ids(self, names_or_aliases: List[str]):
        return [self.name_aliases_to_id[name_or_aliaes] for name_or_aliaes in names_or_aliases]

    def get_main_name(self, class_id: int):
        return self.id_to_name[class_id]

    def get_main_names(self, class_ids: List[int]):
        return [self.id_to_name[class_id] for class_id in class_ids]

    # keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    def filter_labels(
        self,
        required_name_aliaes: List[str] = None,
        required_ids: List[int] = None,
    ) -> Iterator[SingleLabel]:
        if required_name_aliaes and required_ids:
            raise ValueError("required_name_alias and required_ids cannot be both set.")
        if required_name_aliaes:
            required_ids = self.get_class_ids(names_or_aliases=required_name_aliaes)

        for label in self.labels:
            if required_ids is not None and label.id not in required_ids:
                continue

            yield label

    def find_dups(self, new_labels: Any) -> List[str]:
        if type(new_labels) is str:
            new_set = set([new_labels])
        elif type(new_labels) is list:
            new_set = set(new_labels)
        else:
            new_set = set(new_labels.name_aliases_to_id.keys())
        return list(set(self.name_aliases_to_id.keys()) & new_set)

    def to_proto(self) -> backend_pb2.LabelCollection:
        label_dict = self.dict()
        for label in label_dict.get("labels", []):
            label["create_time"] = datetime.timestamp(label["create_time"])
            label["update_time"] = datetime.timestamp(label["update_time"])

        label_collection = backend_pb2.LabelCollection()
        json_format.ParseDict(label_dict, label_collection, ignore_unknown_fields=False)
        return label_collection


def parse_labels_from_proto(label_collection: backend_pb2.LabelCollection) -> UserLabels:
    label_dict = json_format.MessageToDict(label_collection,
                                           preserving_proto_field_name=True,
                                           use_integers_for_enums=True)
    for label in label_dict.get("labels", []):
        label["create_time"] = datetime.fromtimestamp(label["create_time"])
        label["update_time"] = datetime.fromtimestamp(label["update_time"])

    return UserLabels.parse_obj(label_dict)


def default_labels_file_name() -> str:
    return 'labels.yaml'


def get_storage_labels(label_storage_file: str) -> LabelStorage:
    """
    get all labels from label storage file

    Returns:
    LabelStorage: all labels

    Raises:
        FileNotFoundError: if label storage file not found
        ValueError: if version mismatch
        Error: if parse failed or other error occured
    """
    obj = {}
    if os.path.isfile(label_storage_file):
        with open(label_storage_file, 'r') as f:
            obj = yaml.safe_load(f)
    return LabelStorage(**obj)


def merge_labels(label_storage_file: str, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
    # TODO: too hard to read, make it simpler in another pr

    # check `candidate_labels` has no duplicate
    candidate_labels_list = [x.strip().lower().split(",") for x in candidate_labels]
    candidates_list = [x for row in candidate_labels_list for x in row]
    if len(candidates_list) != len(set(candidates_list)):
        logging.error(f"conflict labels: {candidate_labels_list}")
        return candidate_labels_list

    current_time = datetime.now()

    # all labels in storage file
    existed_labels = get_storage_labels(label_storage_file=label_storage_file).labels
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
            label.update_time = current_time
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
                        create_time=current_time,
                        update_time=current_time))
        existed_labels_set.update(candidate_set)

    if not (check_only or conflict_labels):
        label_storage = LabelStorage(labels=existed_labels)
        with open(label_storage_file, 'w') as f:
            yaml.safe_dump(label_storage.dict(), f)
    if conflict_labels:
        logging.error(f"conflict labels: {conflict_labels}")
    return conflict_labels


def create_empty(label_storage_file: str) -> None:
    if os.path.isfile(label_storage_file):
        raise FileExistsError(f"already exists: {label_storage_file}")

    with open(label_storage_file, 'w') as f:
        yaml.safe_dump(LabelStorage().dict(), f)
