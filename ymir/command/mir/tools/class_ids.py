from datetime import datetime
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import fasteners  # type: ignore
from pydantic import BaseModel, root_validator, validate_model, validator
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
        return normalized_name(v)

    @validator('aliases', each_item=True)
    def _strip_and_lower_alias(cls, v: str) -> str:
        return normalized_name(v)


class _LabelStorage(BaseModel):
    version: int = EXPECTED_FILE_VERSION
    labels: List[_SingleLabel] = []
    _label_to_ids: Dict[str, Tuple[int, Optional[str]]] = {}
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
        labels: List[_SingleLabel] = values.get('labels', [])

        # check duplicate
        label_names = []
        for label in labels:
            label_names.append(label.name)
            label_names.extend(label.aliases)
        if len(label_names) != len(set(label_names)):
            raise ClassIdManagerError('duplicated class label names and aliases')
        label_ids = [label.id for label in labels]
        if len(label_ids) != len(set(label_ids)):
            raise ClassIdManagerError('duplicated class label ids')

        label_to_ids: Dict[str, Tuple[int, Optional[str]]] = {}
        id_to_labels: Dict[int, str] = {}
        for label in labels:
            label_to_ids[label.name] = (label.id, None)
            for label_alias in label.aliases:
                label_to_ids[label_alias] = (label.id, label.name)

            id_to_labels[label.id] = label.name

        values['_label_to_ids'] = label_to_ids
        values['_id_to_labels'] = id_to_labels
        return values

    # public: general
    def dict(self) -> Any:  # type: ignore
        return super().dict(exclude={'_label_to_ids', '_id_to_labels'})

    def check(self) -> None:
        """
        force validators to run again, update `_id_to_labels` and `_label_to_ids`
        """
        validation_result, _, validation_error = validate_model(model=self.__class__, input_data=self.__dict__)
        if validation_error:
            raise validation_error

        # this two fields not automatically updated when `validate_model` ends
        self._id_to_labels.update(validation_result.get('_id_to_labels', {}))
        self._label_to_ids.update(validation_result.get('_label_to_ids', {}))


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

        self.__load(ids_file_path(mir_root=mir_root))

    # private: load and unload
    def __load(self, file_path: str) -> bool:
        if not file_path:
            raise ClassIdManagerError('empty path received')
        if self._storage_file_path:
            raise ClassIdManagerError(f"already loaded from: {self._storage_file_path}")

        self.__reload(file_path)

        self._storage_file_path = file_path
        return True

    def __reload(self, file_path: str) -> None:
        with open(file_path, 'r') as f:
            file_obj = yaml.safe_load(f)
        if file_obj is None:
            file_obj = {}

        self._label_storage = _LabelStorage(**file_obj)

    def __save(self) -> None:
        if not self._storage_file_path:
            raise ClassIdManagerError('not loaded')

        with open(self._storage_file_path, 'w') as f:
            yaml.safe_dump(self._label_storage.dict(), f)

    # public: general
    def id_and_main_name_for_name(self, name: str) -> Tuple[int, Optional[str]]:
        """
        returns type id and main type name for main type name or alias

        Args:
            name (str): main type name or alias

        Raises:
            ClassIdManagerError: if not loaded, or name is empty

        Returns:
            Tuple[int, Optional[str]]: (type id, main type name),
            if name not found, returns -1, None
        """
        name = normalized_name(name)
        if not self._storage_file_path:
            raise ClassIdManagerError("not loaded")
        if not name:
            raise ClassIdManagerError("empty name")

        if name not in self._label_storage._label_to_ids:
            return -1, None

        return self._label_storage._label_to_ids[name]

    def main_name_for_id(self, type_id: int) -> Optional[str]:
        """
        get main type name for type id, if not found, returns None

        Args:
            type_id (int): type id

        Returns:
            Optional[str]: corresponding main type name, if not found, returns None
        """
        return self._label_storage._id_to_labels.get(type_id, None)

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
        return list(self._label_storage._id_to_labels.values())

    def all_ids(self) -> List[int]:
        """
        Returns:
            List[int]: all class_ids, if not loaded, returns empty list
        """
        return list(self._label_storage._id_to_labels.keys())

    def size(self) -> int:
        """
        Returns:
            int: size of all type ids and main names, if not loaded, returns 0
        """
        return len(self._label_storage._id_to_labels)

    def has_name(self, name: str) -> bool:
        return normalized_name(name) in self._label_storage._label_to_ids

    def has_id(self, type_id: int) -> bool:
        return type_id in self._label_storage._id_to_labels

    def add(self, main_name: str) -> int:
        main_name = normalized_name(main_name)
        if not main_name:
            raise ClassIdManagerError('invalid main class name')

        with fasteners.InterProcessLock(path=parse_label_lock_path_or_link(self._storage_file_path)):
            self.__reload(self._storage_file_path)

            current_datetime = datetime.now()
            added_class_id = self.size()

            single_label = _SingleLabel(id=added_class_id, name=main_name)
            single_label.create_time = current_datetime
            single_label.update_time = current_datetime
            self._label_storage.labels.append(single_label)
            self._label_storage.check()
            self.__save()

            return added_class_id


def normalized_name(name: str) -> str:
    return name.lower().strip()
