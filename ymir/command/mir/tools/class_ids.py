from datetime import datetime
import os
from typing import Dict, List, Optional, Set, Tuple

import fasteners  # type: ignore
from pydantic import BaseModel, root_validator, validator
import yaml

from mir.tools import utils as mir_utils

EXPECTED_FILE_VERSION = 1


class _SingleLabel(BaseModel):
    id: int
    name: str
    create_time: datetime = datetime(year=2022, month=1, day=1)
    update_time: datetime = datetime(year=2022, month=1, day=1)
    aliases: List[str] = []

    @validator('name')
    def _strip_and_lower_name(cls, v: str) -> str:
        return _normalize_and_check_name(v)

    @validator('aliases', each_item=True)
    def _strip_and_lower_alias(cls, v: str) -> str:
        return _normalize_and_check_name(v)


class _LabelStorage(BaseModel):
    version: int = EXPECTED_FILE_VERSION
    labels: List[_SingleLabel] = []
    _label_to_ids: Dict[str, Tuple[int, str]] = {}  # store main_name for main_name/alias lookup.
    _id_to_labels: Dict[int, str] = {}

    # protected: validators
    @validator('version')
    def _check_version(cls, v: int) -> int:
        if v != EXPECTED_FILE_VERSION:
            raise ValueError(f"incorrect version: {v}, needed {EXPECTED_FILE_VERSION}")
        return v

    @validator('labels')
    def _check_labels(cls, labels: List[_SingleLabel]) -> List[_SingleLabel]:
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

    @root_validator
    def _generate_dicts(cls, values: dict) -> dict:
        labels: List[_SingleLabel] = values['labels']

        label_to_ids: Dict[str, Tuple[int, str]] = {}
        id_to_labels: Dict[int, str] = {}
        for label in labels:
            label_to_ids[label.name] = (label.id, label.name)
            for label_alias in label.aliases:
                label_to_ids[label_alias] = (label.id, label.name)

            id_to_labels[label.id] = label.name

        values['_label_to_ids'] = label_to_ids
        values['_id_to_labels'] = id_to_labels
        return values

    # public: general
    def dict(self) -> Dict:  # type: ignore
        return super().dict(exclude={'_label_to_ids', '_id_to_labels'})

    def add_new_label(self, name: str) -> Tuple[int, str]:
        name = _normalize_and_check_name(name)
        if name in self._label_to_ids:
            return self._label_to_ids[name]

        current_datetime = datetime.now()
        added_class_id = len(self.labels)
        single_label = _SingleLabel(id=added_class_id, name=name)
        single_label.create_time = current_datetime
        single_label.update_time = current_datetime
        self.labels.append(single_label)

        # update lookup dict.
        self._label_to_ids[name] = added_class_id, name
        self._id_to_labels[added_class_id] = name

        return added_class_id, name

    def id_to_label(self, type_id: int) -> Optional[str]:
        """
        get main type name for type id, if not found, returns None

        Args:
            type_id (int): type id

        Returns:
            Optional[str]: corresponding main type name, if not found, returns None
        """
        return self._id_to_labels.get(type_id, None)

    def label_to_id_name(self, type_label: str) -> Tuple[int, str]:
        """
        returns type id and main type name for main type name or alias

        Args:
            name (str): main type name or alias

        Returns:
            Tuple[int, str]: (type id, main type name),
            if name not found, returns (-1, name)
        """
        type_label = _normalize_and_check_name(type_label)
        return self._label_to_ids.get(type_label, (-1, type_label))

    @property
    def all_main_names(self) -> List[str]:
        return list(self._id_to_labels.values())

    @property
    def all_ids(self) -> List[int]:
        return list(self._id_to_labels.keys())


def ids_file_name() -> str:
    return 'labels.yaml'


def ids_file_path(mir_root: str) -> str:
    return os.path.join(mir_utils.repo_dot_mir_path(mir_root=mir_root), ids_file_name())


def parse_label_lock_path_or_link(ids_storage_file_path: str) -> str:
    # for ymir-command users, file_path points to a real file
    # for ymir-controller users, file_path points to a link, need to lock all write request for user
    file_path = ids_storage_file_path
    if os.path.islink(file_path):
        file_path = os.path.realpath(file_path)
    lock_file_path = os.path.join(os.path.dirname(file_path), 'labels.lock')
    return lock_file_path


def create_empty_if_not_exists(mir_root: str) -> None:
    file_path = ids_file_path(mir_root=mir_root)
    if os.path.isfile(file_path):
        return

    label_storage = _LabelStorage()
    with open(file_path, 'w') as f:
        yaml.safe_dump(label_storage.dict(), f)


class ClassIdManagerError(BaseException):
    pass


class ClassIdManager(object):
    """
    a query tool for label storage file
    """
    __slots__ = ("_storage_file_path", "_label_storage")

    # life cycle
    def __init__(self, mir_root: str) -> None:
        super().__init__()

        # it will have value iff successfully loaded
        self._storage_file_path = ''

        if not self.__load(ids_file_path(mir_root=mir_root)):
            raise ClassIdManagerError("ClassIdManager initialize failed in mir_root: {mir_root}")

    # private: load and unload
    def __load(self, file_path: str) -> bool:
        if not file_path:
            raise ClassIdManagerError('ClassIdManager: empty path received')

        self._storage_file_path = file_path
        self.__reload()

        return True

    def __reload(self) -> None:
        with open(self._storage_file_path, 'r') as f:
            file_obj = yaml.safe_load(f)
        if file_obj is None:
            file_obj = {}

        self._label_storage = _LabelStorage(**file_obj)

    def __save(self) -> None:
        with open(self._storage_file_path, 'w') as f:
            yaml.safe_dump(self._label_storage.dict(), f)

    # public: general
    def id_and_main_name_for_name(self, name: str) -> Tuple[int, str]:
        return self._label_storage.label_to_id_name(name)

    def main_name_for_id(self, type_id: int) -> Optional[str]:
        return self._label_storage.id_to_label(type_id)

    def id_for_names(self, names: List[str]) -> Tuple[List[int], List[str]]:
        """
        return all type ids for names

        Args:
            names (List[str]): main type names or alias

        Returns:
            Tuple[List[int], List[str]]: corresponding type ids and unknown names
        """
        class_ids = []
        unknown_names = []
        for name in names:
            class_id = self.id_and_main_name_for_name(name=name)[0]
            class_ids.append(class_id)

            if class_id < 0:
                unknown_names.append(name)

        return class_ids, unknown_names

    def all_main_names(self) -> List[str]:
        """
        Returns:
            List[str]: all main names, if not loaded, returns empty list
        """
        return self._label_storage.all_main_names

    def all_ids(self) -> List[int]:
        """
        Returns:
            List[int]: all class_ids, if not loaded, returns empty list
        """
        return self._label_storage.all_ids

    def has_name(self, name: str) -> bool:
        return (self.id_and_main_name_for_name(name=name)[0] >= 0)

    def has_id(self, type_id: int) -> bool:
        return (self.main_name_for_id(type_id=type_id) is not None)

    def add_main_name(self, main_name: str) -> Tuple[int, str]:
        # only trigger reload at saving, not read safe, main_name may already been added in another process.
        self.__reload()
        if self.has_name(main_name):
            return self.id_and_main_name_for_name(main_name)

        with fasteners.InterProcessLock(path=parse_label_lock_path_or_link(self._storage_file_path)):
            added_class_id, main_name = self._label_storage.add_new_label(name=main_name)
            self.__save()
            return added_class_id, main_name


def _normalize_and_check_name(name: str) -> str:
    name = name.lower().strip()
    if not name:
        raise ValueError("get empty normalized name")
    return name
