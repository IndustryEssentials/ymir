import csv
import os
from typing import Dict, List, Optional, Tuple


def ids_file_name() -> str:
    return 'labels.csv'


def ids_file_path(mir_root: str) -> str:
    file_path = os.path.join(mir_root, ids_file_name())
    return file_path


class ClassIdManagerError(BaseException):
    pass


class ClassIdManager(object):
    """
    a query tool for file `labels.csv`, which has following format in each line:
        type id, preserved, main type name, alias 1, alias 2, ...
    """
    __slots__ = ("_csv_path", "_type_name_id_dict", "_type_id_name_dict")

    # life cycle
    def __init__(self, mir_root: str) -> None:
        super().__init__()

        # it will have value iff successfully loaded
        self._csv_path = ''
        # key: main type name or alias, value: (type id, None for main type name, or main name for alias)
        self._type_name_id_dict = {}  # type: Dict[str, Tuple[int, Optional[str]]]
        # key: type id, value: main type name
        self._type_id_name_dict = {}  # type: Dict[int, str]

        self.__load(ids_file_path(mir_root=mir_root))

    # private: load and unload
    def __load(self, csv_path: str) -> bool:
        if not csv_path:
            raise ClassIdManagerError('empty path received')
        if self._csv_path:
            raise ClassIdManagerError(f"already loaded from: {self._csv_path}")

        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f)
            for line_components in csv_reader:
                if len(line_components) <= 2:
                    continue  # empty lines also ignored here
                if line_components[0].startswith('#'):
                    continue

                type_id = int(line_components[0])

                main_type_name = None

                # for single line, parse type id, main type name, alias
                for type_name_idx, type_name in enumerate(line_components[2:]):
                    type_name = type_name.strip().lower()

                    # handle error situations
                    if type_name in self._type_name_id_dict:
                        previous_pair = self._type_name_id_dict[type_name]
                        raise ClassIdManagerError("dumplicate type name: {}, previous: {}, now: {}".format(
                            type_name, previous_pair[0], type_id))
                    if not type_name:
                        raise ClassIdManagerError("empty type name for type id: {}".format(type_id))

                    if type_name_idx == 0:
                        # if it's main type name
                        main_type_name = type_name
                        self._type_name_id_dict[main_type_name] = (type_id, None)
                        self._type_id_name_dict[type_id] = main_type_name
                    else:
                        # if it's alias
                        self._type_name_id_dict[type_name] = (type_id, main_type_name)

        # save `self._csv_path` as a flag of successful loading
        self._csv_path = csv_path
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
        name = name.strip()
        if not self._csv_path:
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
        type_ids = []
        for name in names:
            type_ids.append(self.id_and_main_name_for_name(name=name)[0])
        return type_ids

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
        return name in self._type_name_id_dict

    def has_id(self, type_id: int) -> bool:
        return type_id in self._type_id_name_dict
