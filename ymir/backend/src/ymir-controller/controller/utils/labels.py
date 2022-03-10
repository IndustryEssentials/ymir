from collections import Counter
from pathlib import Path
import os
import time
from typing import Dict, List, Iterable, Set

from pydantic import BaseModel
import yaml


EXPECTED_FILE_VERSION = 1


def labels_file_name() -> str:
    return 'labels.yaml'


def labels_file_path(mir_root: str) -> str:
    file_dir = os.path.join(mir_root, '.mir')
    os.makedirs(file_dir, exist_ok=True)
    return os.path.join(file_dir, labels_file_name())


class SingleLabel(BaseModel):
    id: int
    name: str
    created: float = 0
    modified: float = 0
    aliases: List[str] = []


class _LabelStorage(BaseModel):
    version: int
    labels: List[SingleLabel] = []


class LabelFileHandler:
    def __init__(self, mir_root: str) -> None:
        self._label_file = labels_file_path(mir_root=mir_root)

        # create if not exists
        Path(self._label_file).touch(exist_ok=True)

    def get_label_file_path(self) -> str:
        return self._label_file

    def _write_label_file(self, all_labels: List[SingleLabel]) -> None:
        """
        dump all label content into a label storage file, old file contents will be lost
        Args:
            all_labels (List[dict]): all labels, for each element: id, name, aliases, created, modified
        """
        label_storage = _LabelStorage(version=EXPECTED_FILE_VERSION, labels=all_labels)
        with open(self._label_file, 'w') as f:
            yaml.safe_dump(label_storage.dict(), f)

    def get_all_labels(self) -> List[SingleLabel]:
        """
        get all labels from label storage file

        Returns:
        List[dict]: all label infos, each element is dict with the following kvs:
            id: label_id, int
            name: main name, str
            aliases: aliases list, list of str
            created: created timestamp, float
            modified: modified timestamp, float

        Raises:
            FileNotFoundError: if label storage file not found
            ValueError: if version mismatch
            Error: if parse failed or other error occured
        """
        with open(self._label_file, 'r') as f:
            obj = yaml.safe_load(f)
        # if empty file, returns empty list
        if not obj:
            return []

        label_storage = _LabelStorage(**obj)
        if label_storage.version != EXPECTED_FILE_VERSION:
            raise ValueError(f"version mismatch: expected: {EXPECTED_FILE_VERSION} != actual: {label_storage.version}")

        label_names_set: Set[str] = set()  # use to check dumplicate label names
        for label in label_storage.labels:
            # use stripped lower case for each label
            label.name = label.name.strip().lower()
            label.aliases = [v.strip().lower() for v in label.aliases]

            # check label name dumplicate and inline dumplicate
            if label.name in label_names_set:
                raise ValueError(f"dumplicated label name: {label.name}")
            name_and_aliases = label.aliases + [label.name]
            if len(name_and_aliases) != len(set(name_and_aliases)):
                raise ValueError(f"dumplicated inline label: {name_and_aliases}")
            label_names_set.add(label.name)

        return label_storage.labels

    def merge_labels(self, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
        # check `candidate_labels` has no duplicate
        candidate_labels_list = [x.strip().lower().split(",") for x in candidate_labels]
        candidates_list = [x for row in candidate_labels_list for x in row]
        if len(candidates_list) != len(set(candidates_list)):
            return candidate_labels_list

        current_timestamp = time.time()

        # all labels in storage file, for each element: id, name, aliases (optional), created, modified
        existed_labels = self.get_all_labels()
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
                label.modified = current_timestamp
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
                            created=current_timestamp,
                            modified=current_timestamp))
            existed_labels_set.update(candidate_set)

        if not (check_only or conflict_labels):
            self._write_label_file(existed_labels)
        return conflict_labels

    def get_main_labels_by_ids(self, type_ids: Iterable) -> List[str]:
        all_labels = self.get_all_labels()
        return [all_labels[int(idx)].name for idx in type_ids]
