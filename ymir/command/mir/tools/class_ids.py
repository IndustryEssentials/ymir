import os
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, validator, root_validator
import yaml

from mir.tools import utils as mir_utils

EXPECTED_FILE_VERSION = 1


class _SingleLabel(BaseModel):
    id: int
    name: str
    aliases: List[str] = []

    @validator('name')
    def _strip_and_lower_name(cls, v: str) -> str:
        return v.strip().lower()

    @validator('aliases', each_item=True)
    def _strip_and_lower_alias(cls, v: str) -> str:
        return v.strip().lower()


class _LabelStorage(BaseModel):
    version: int = EXPECTED_FILE_VERSION
    labels: List[_SingleLabel] = []
    _label_to_ids: Dict[str, Tuple[int, Optional[str]]] = {}
    _id_to_labels: Dict[int, str] = {}

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
        label_to_ids: Dict[str, Tuple[int, Optional[str]]] = {}
        id_to_labels: Dict[int, str] = {}
        for label in labels:
            _set_if_not_exists(k=label.name, v=(label.id, None), d=label_to_ids, error_message_prefix='duplicated name')
            #   key: aliases
            for label_alias in label.aliases:
                _set_if_not_exists(k=label_alias,
                                   v=(label.id, label.name),
                                   d=label_to_ids,
                                   error_message_prefix='duplicated alias')

            # self._type_id_name_dict
            _set_if_not_exists(k=label.id, v=label.name, d=id_to_labels, error_message_prefix='duplicated id')

        values['_label_to_ids'] = label_to_ids
        values['_id_to_labels'] = id_to_labels
        return values


def ids_file_name() -> str:
    return 'labels.yaml'


def ids_file_path(mir_root: str) -> str:
    return os.path.join(mir_utils.repo_dot_mir_path(mir_root=mir_root), ids_file_name())


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

        with open(file_path, 'r') as f:
            file_obj = yaml.safe_load(f)
        if file_obj is None:
            file_obj = {}

        self._label_storage = _LabelStorage(**file_obj)
        # save `self._storage_file_path` as a flag of successful loading
        self._storage_file_path = file_path
        return True

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
        name = name.strip().lower()
        if not self._storage_file_path:
            raise ClassIdManagerError("not loade")
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
        return name.strip().lower() in self._label_storage._label_to_ids

    def has_id(self, type_id: int) -> bool:
        return type_id in self._label_storage._id_to_labels


def _set_if_not_exists(k: Any, v: Any, d: dict, error_message_prefix: str) -> None:
    if k in d:
        raise ClassIdManagerError(f"{error_message_prefix}: {k}")
    d[k] = v
