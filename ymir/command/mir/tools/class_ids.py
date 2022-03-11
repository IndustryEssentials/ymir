import os
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, validator
import yaml

from mir.tools import utils as mir_utils


EXPECTED_FILE_VERSION = 1


class _SingleLabel(BaseModel):
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


class _LabelStorage(BaseModel):
    version: int = EXPECTED_FILE_VERSION
    labels: List[_SingleLabel] = []

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
    __slots__ = ("_file_path", "_type_name_id_dict", "_type_id_name_dict")

    # life cycle
    def __init__(self, mir_root: str) -> None:
        super().__init__()

        # it will have value iff successfully loaded
        self._file_path = ''
        # key: main type name or alias, value: (type id, None for main type name, or main name for alias)
        self._type_name_id_dict = {}  # type: Dict[str, Tuple[int, Optional[str]]]
        # key: type id, value: main type name
        self._type_id_name_dict = {}  # type: Dict[int, str]

        self.__load(ids_file_path(mir_root=mir_root))

    # private: load and unload
    def __load(self, file_path: str) -> bool:
        if not file_path:
            raise ClassIdManagerError('empty path received')
        if self._file_path:
            raise ClassIdManagerError(f"already loaded from: {self._file_path}")

        with open(file_path, 'r') as f:
            file_obj = yaml.safe_load(f)
        if file_obj is None:
            file_obj = {}

        label_storage = _LabelStorage(**file_obj)
        labels = label_storage.labels
        for label in labels:
            # self._type_name_id_dict
            #   key: main label name
            self._set_if_not_exists(k=label.name,
                                    v=(label.id, None),
                                    d=self._type_name_id_dict,
                                    error_message_prefix='duplicated name')
            #   key: aliases
            for label_alias in label.aliases:
                self._set_if_not_exists(k=label_alias,
                                        v=(label.id, label.name),
                                        d=self._type_name_id_dict,
                                        error_message_prefix='duplicated alias')

            # self._type_id_name_dict
            self._set_if_not_exists(k=label.id,
                                    v=label.name,
                                    d=self._type_id_name_dict,
                                    error_message_prefix='duplicated id')

        # save `self._file_path` as a flag of successful loading
        self._file_path = file_path
        return True

    # public: general
    def id_and_main_name_for_name(self, name: str) -> Tuple[int, Optional[str]]:
        """
        returns type id and main type name for main type name or alias

        Args:
            name (str): main type name or alias

        Raises:
            ClassIdManagerError: if not loaded, or name is empty, or can not find name

        Returns:
            Tuple[int, Optional[str]]: (type id, main type name)
        """
        name = name.strip().lower()
        if not self._file_path:
            raise ClassIdManagerError("not loade")
        if not name:
            raise ClassIdManagerError("empty name")

        if name not in self._type_name_id_dict:
            raise ClassIdManagerError(f"not exists: {name}")

        return self._type_name_id_dict[name]

    def main_name_for_id(self, type_id: int) -> Optional[str]:
        """
        get main type name for type id, if not found, returns None

        Args:
            type_id (int): type id

        Returns:
            Optional[str]: corresponding main type name, if not found, returns None
        """
        return self._type_id_name_dict.get(type_id, None)

    def id_for_names(self, names: List[str]) -> List[int]:
        """
        return all type ids for names

        Args:
            names (List[str]): main type names or alias

        Returns:
            List[int]: corresponding type ids
        """
        return [self.id_and_main_name_for_name(name=name)[0] for name in names]

    def all_main_names(self) -> List[str]:
        """
        Returns:
            List[str]: all main names, if not loaded, returns empty list
        """
        return list(self._type_id_name_dict.values())

    def size(self) -> int:
        """
        Returns:
            int: size of all type ids and main names, if not loaded, returns 0
        """
        return len(self._type_id_name_dict)

    def has_name(self, name: str) -> bool:
        return name.strip().lower() in self._type_name_id_dict

    def has_id(self, type_id: int) -> bool:
        return type_id in self._type_id_name_dict

    @classmethod
    def _set_if_not_exists(cls, k: Any, v: Any, d: dict, error_message_prefix: str) -> None:
        if k in d:
            raise ClassIdManagerError(f"{error_message_prefix}: {k}")
        d[k] = v
