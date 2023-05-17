from datetime import datetime
import os
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

import fasteners  # type: ignore
from mir.version import check_ymir_version_or_crash, YMIR_REPO_VERSION
from pydantic import BaseModel, root_validator, validator, validate_model
import yaml


class SingleLabel(BaseModel):
    id: int = -1
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


class LabelStorage(BaseModel):
    labels: List[SingleLabel] = []
    ymir_version: str = YMIR_REPO_VERSION

    # protected: validators
    @validator('ymir_version')
    def _check_version(cls, v: str) -> str:
        check_ymir_version_or_crash(v)
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
    _id_to_name: Dict[int, str] = {}
    _name_aliases_to_id: Dict[str, int] = {}
    storage_file: Optional[str] = None

    @root_validator
    def _generate_dicts(cls, values: dict) -> dict:
        # source priority: storage_file > labels.
        # in most cases, UserLabels is bind to a storage_file.
        storage_file = values.get("storage_file")
        if storage_file and os.path.isfile(storage_file):
            with open(storage_file, 'r') as f:
                file_obj = yaml.safe_load(f)
            if file_obj is None:
                file_obj = {}
            values["labels"] = LabelStorage(**file_obj).labels

        name_aliases_to_id: Dict[str, int] = {}
        id_to_name: Dict[int, str] = {}
        for label in values['labels']:
            name_aliases_to_id[label.name] = label.id
            for label_alias in label.aliases:
                name_aliases_to_id[label_alias] = label.id

            id_to_name[label.id] = label.name

        values['_name_aliases_to_id'] = name_aliases_to_id
        values['_id_to_name'] = id_to_name
        return values

    def __reload(self) -> None:
        if not (self.storage_file and os.path.isfile(self.storage_file)):
            raise RuntimeError("cannot reload with empty storage_file.")

        *_, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error

    def __save(self) -> None:
        if not self.storage_file:
            raise RuntimeError("empty storage_file.")

        with open(self.storage_file, 'w') as f:
            yaml.safe_dump(self.dict(), f)

    def _add_new_cname(self, name: str, exist_ok: bool = True) -> Tuple[int, str]:
        name = _normalize_and_check_name(name)
        if name in self._name_aliases_to_id:
            if not exist_ok:
                raise ValueError("{name} already exists in userlabels.")
            cid = self._name_aliases_to_id[name]
            return (cid, self._id_to_name[cid])

        current_datetime = datetime.now()
        added_class_id = len(self.labels)
        self.labels.append(
            SingleLabel(
                id=added_class_id,
                name=name,
                create_time=current_datetime,
                update_time=current_datetime,
            ))

        # update lookup dict.
        self._name_aliases_to_id[name] = added_class_id
        self._id_to_name[added_class_id] = name

        return added_class_id, name

    class Config:
        fields = {'labels': {'include': True}, 'ymir_version': {'include': True}}

    # public interfaces.
    def id_and_main_name_for_name(self, name: str) -> Tuple[int, str]:
        name = _normalize_and_check_name(name)
        id = self._name_aliases_to_id.get(name, -1)
        name = self._id_to_name.get(id, name)
        return (id, name)

    def id_for_names(self,
                     names: Union[str, List[str]],
                     drop_unknown_names: bool = False,
                     raise_if_unknown: bool = False) -> Tuple[List[int], List[str]]:
        if isinstance(names, str):
            names = [names]

        class_ids: List[int] = []
        unknown_names: List[str] = []
        for name in names:
            class_id, cname = self.id_and_main_name_for_name(name=name)
            if class_id >= 0:
                class_ids.append(class_id)
            else:
                unknown_names.append(cname)
                if not drop_unknown_names:
                    class_ids.append(class_id)

        if raise_if_unknown and unknown_names:
            raise ValueError(f"unknown class found: {unknown_names}")

        return class_ids, unknown_names

    def main_name_for_id(self, class_id: int) -> str:
        if class_id not in self._id_to_name:
            raise ValueError(f"copy: unknown src class id: {class_id}")
        return self._id_to_name[class_id]

    def main_name_for_ids(self, class_ids: List[int]) -> List[str]:
        return [self.main_name_for_id(class_id) for class_id in class_ids]

    def all_main_names(self) -> List[str]:
        return list(self._id_to_name.values())

    def all_main_name_aliases(self) -> List[str]:
        return list(self._name_aliases_to_id.keys())

    def all_ids(self) -> List[int]:
        return list(self._id_to_name.keys())

    def has_name(self, name: str) -> bool:
        return self.id_for_names(name)[0][0] >= 0

    def has_id(self, cid: int) -> bool:
        return cid in self._id_to_name

    def add_main_name(self, main_name: str) -> Tuple[int, str]:
        return self.add_main_names([main_name])[0]

    def add_main_names(self, main_names: List[str]) -> List[Tuple[int, str]]:
        # only trigger reload at saving, not read safe, main_name may already been added in another process.
        self.__reload()
        ret_val: List[Tuple[int, str]] = []

        # shortcut, return if all names are known.
        for main_name in main_names:
            class_id, main_name = self.id_and_main_name_for_name(main_name)
            if class_id < 0:
                break
            ret_val.append((class_id, main_name))
        if len(ret_val) == len(main_names):  # all known names.
            return ret_val

        if not self.storage_file:
            raise RuntimeError("empty storage_file.")

        ret_val.clear()
        with fasteners.InterProcessLock(path=os.path.realpath(self.storage_file) + '.lock'):
            for main_name in main_names:
                added_class_id, main_name = self._add_new_cname(name=main_name)
                ret_val.append((added_class_id, main_name))
            self.__save()
        return ret_val

    def upsert_labels(self, new_labels: "UserLabels", check_only: bool = False) -> "UserLabels":
        """
        update or insert new_labels, return labels that are failed to add
        """
        if not self.storage_file:
            raise RuntimeError("empty storage_file.")

        self.__reload()
        with fasteners.InterProcessLock(path=os.path.realpath(self.storage_file) + '.lock'):
            current_time = datetime.now()

            conflict_labels = []
            for label in new_labels.labels:
                new_label = SingleLabel.parse_obj(label.dict())
                idx = self.id_and_main_name_for_name(label.name)[0]

                # in case any alias is in other labels.
                conflict_alias = []
                for alias in label.aliases:
                    alias_idx = self.id_and_main_name_for_name(alias)[0]
                    if alias_idx >= 0 and alias_idx != idx:
                        conflict_alias.append(alias)
                if conflict_alias:
                    new_label.id = -1
                    conflict_labels.append(new_label)
                    continue

                new_label.update_time = current_time
                if idx >= 0:  # update alias.
                    new_label.id = idx
                    new_label.create_time = self.labels[idx].create_time
                    self.labels[idx] = new_label
                else:  # insert new record.
                    new_label.id = len(self.labels)
                    new_label.create_time = current_time
                    self.labels.append(new_label)

            if not (check_only or conflict_labels):
                self.__save()

            return UserLabels(labels=conflict_labels)

    def find_dups(self, new_labels: Union[str, List, "UserLabels"]) -> List[str]:
        if isinstance(new_labels, str):
            new_set = {new_labels}
        elif isinstance(new_labels, list):
            new_set = set(new_labels)
        elif isinstance(new_labels, type(self)):
            new_set = set(new_labels.all_main_name_aliases())
        return list(set(self.all_main_name_aliases()) & new_set)

    # keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    def filter_labels(
        self,
        required_name_aliaes: List[str] = None,
        required_ids: List[int] = None,
    ) -> Iterator[SingleLabel]:
        if required_name_aliaes and required_ids:
            raise ValueError("required_name_alias and required_ids cannot be both set.")
        if required_name_aliaes:
            required_ids = self.id_for_names(names=required_name_aliaes, raise_if_unknown=True)[0]

        for label in self.labels:
            if required_ids is None or label.id in required_ids:
                yield label


def ids_file_name() -> str:
    return 'labels.yaml'


def ids_file_path(mir_root: str) -> str:
    mir_dir = os.path.join(mir_root, '.mir')
    os.makedirs(mir_dir, exist_ok=True)
    return os.path.join(mir_dir, ids_file_name())


def load_or_create_userlabels(label_storage_file: str,
                              create_ok: bool = False) -> UserLabels:
    if not label_storage_file:
        raise ValueError("empty label_storage_file")

    if os.path.isfile(label_storage_file):
        return UserLabels(storage_file=label_storage_file)

    if not create_ok:
        raise RuntimeError(f"label file miss in path: {label_storage_file}")

    os.makedirs(os.path.dirname(label_storage_file), exist_ok=True)
    user_labels = UserLabels()
    with open(label_storage_file, 'w') as f:
        yaml.safe_dump(user_labels.dict(), f)
    return user_labels


def _normalize_and_check_name(name: str) -> str:
    name = name.lower().strip()
    if not name:
        raise ValueError("get empty normalized name")
    return name
