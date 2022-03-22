from datetime import datetime
import logging
import os
from typing import Any, Dict, Iterator, List, Set, Union

from google.protobuf import json_format
from pydantic import BaseModel, root_validator, validator
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

    @root_validator()
    def fill_lookup_tables(cls, values: Any):
        for label in values["labels"]:
            values["id_to_name"][label.id] = label.name
            values["name_to_id"][label.name] = label.id
            values["name_aliases_to_id"][label.name] = label.id
            for alias in label.aliases:
                values["name_aliases_to_id"][alias] = label.id
        return values

    class Config:
        fields = {'labels': {'include': True}}

    def get_class_ids(self, names_or_aliases: Union[str, List[str]]) -> List[int]:
        if isinstance(names_or_aliases, str):
            return [self.name_aliases_to_id[names_or_aliases]]
        elif isinstance(names_or_aliases, list):
            return [self.name_aliases_to_id[name_or_aliaes] for name_or_aliaes in names_or_aliases]
        else:
            raise ValueError(f"unsupported type: {type(names_or_aliases)}")

    def get_main_names(self, class_ids: Union[int, List[int]]) -> List[str]:
        if isinstance(class_ids, int):
            return [self.id_to_name[class_ids]]
        elif isinstance(class_ids, list):
            return [self.id_to_name[class_id] for class_id in class_ids]
        else:
            raise ValueError(f"unsupported type: {type(class_ids)}")

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
            if required_ids is None or label.id in required_ids:
                yield label

    def find_dups(self, new_labels: Any) -> List[str]:
        if isinstance(new_labels, str):
            new_set = {new_labels}
        elif isinstance(new_labels, list):
            new_set = set(new_labels)
        elif isinstance(new_labels, type(self)):
            new_set = set(new_labels.name_aliases_to_id.keys())
        else:
            raise ValueError(f"unsupported type: {type(new_labels)}")
        return list(set(self.name_aliases_to_id.keys()) & new_set)

    def to_proto(self) -> backend_pb2.LabelCollection:
        return json_format.Parse(self.json(), backend_pb2.LabelCollection(), ignore_unknown_fields=False)


def merge_labels(label_storage_file: str,
                 new_labels: UserLabels,
                 check_only: bool = False) -> UserLabels:
    current_labels = get_user_labels_from_storage(label_storage_file)
    current_time = datetime.now()

    conflict_labels = []
    for label in new_labels.labels:
        new_label = SingleLabel.parse_obj(label.dict())
        idx = current_labels.name_to_id.get(label.name, None)

        # in case any alias is in other labels.
        conflict_alias = []
        for alias in label.aliases:
            alias_idx = current_labels.name_aliases_to_id.get(alias, idx)
            if alias_idx != idx:
                conflict_alias.append(alias)
        if conflict_alias:
            new_label.id = -1
            conflict_labels.append(new_label)
            continue

        new_label.update_time = current_time
        if idx is not None:  # update alias.
            new_label.id = idx
            new_label.create_time = current_labels.labels[idx].create_time
            current_labels.labels[idx] = new_label
        else:  # insert new record.
            new_label.id = len(current_labels.labels)
            new_label.create_time = current_time
            current_labels.labels.append(new_label)

    if not (check_only or conflict_labels):
        label_storage = LabelStorage(labels=current_labels.labels)
        with open(label_storage_file, 'w') as f:
            yaml.safe_dump(label_storage.dict(), f)

    logging.info(f"conflict labels: {conflict_labels}")
    return UserLabels(labels=conflict_labels)


def parse_labels_from_proto(label_collection: backend_pb2.LabelCollection) -> UserLabels:
    label_dict = json_format.MessageToDict(label_collection,
                                           preserving_proto_field_name=True,
                                           use_integers_for_enums=True)

    return UserLabels.parse_obj(label_dict)


def default_labels_file_name() -> str:
    return 'labels.yaml'


def get_user_labels_from_storage(label_storage_file: str) -> UserLabels:
    """
    get all labels from label storage file

    Returns:
    UserLabels: all labels

    Raises:
        FileNotFoundError: if label storage file not found
        ValueError: if version mismatch
        Error: if parse failed or other error occured
    """
    obj = {}
    if os.path.isfile(label_storage_file):
        with open(label_storage_file, 'r') as f:
            obj = yaml.safe_load(f)
    return UserLabels(**obj)


def create_empty(label_storage_file: str) -> None:
    if os.path.isfile(label_storage_file):
        raise FileExistsError(f"already exists: {label_storage_file}")

    with open(label_storage_file, 'w') as f:
        yaml.safe_dump(LabelStorage().dict(), f)
