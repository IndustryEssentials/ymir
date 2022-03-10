import os
from typing import Any, Dict, List, Optional, Tuple

import yaml


EXPECTED_FILE_VERSION = 1

kVersion = 'version'
kLabels = 'labels'
kLabelName = 'name'
kLabelId = 'id'
kLabelAliases = 'aliases'


def ids_file_name() -> str:
    return 'labels.yaml'


def ids_file_path(mir_root: str) -> str:
    file_dir = os.path.join(mir_root, '.mir')
    os.makedirs(file_dir, exist_ok=True)
    return os.path.join(file_dir, ids_file_name())


def create_empty_if_not_exists(mir_root: str) -> None:
    file_path = ids_file_path(mir_root=mir_root)
    if os.path.isfile(file_path):
        return

    with open(file_path, 'w') as f:
        file_obj = {kVersion: EXPECTED_FILE_VERSION, kLabels: []}
        yaml.safe_dump(file_obj, f)


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
            labels = file_obj.get(kLabels, [])
            for label in labels:
                # key: id, name, alias are used here
                label_id: int = label[kLabelId]
                label_name: str = label[kLabelName].strip().lower()
                label_aliases: List[str] = label.get(kLabelAliases, [])
                if not isinstance(label_aliases, list):
                    raise ClassIdManagerError(f"alias error for id: {label_id}, name: {label_name}")

                label_aliases = [v.strip().lower() for v in label_aliases]

                # self._type_name_id_dict
                #   key: main label name
                self._set_if_not_exists(k=label_name,
                                        v=(label_id, None),
                                        d=self._type_name_id_dict,
                                        error_message_prefix='dumplicated name')
                #   key: aliases
                for label_alias in label_aliases:
                    self._set_if_not_exists(k=label_alias,
                                            v=(label_id, label_name),
                                            d=self._type_name_id_dict,
                                            error_message_prefix='dumplicated alias')

                # self._type_id_name_dict
                self._set_if_not_exists(k=label_id,
                                        v=label_name,
                                        d=self._type_id_name_dict,
                                        error_message_prefix='dumplicated id')

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
