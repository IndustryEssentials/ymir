import csv
import logging
import os
from collections import Counter
from pathlib import Path
import time
from typing import Dict, List, Iterable, Set

import yaml


EXPECTED_FILE_VERSION = 1

kVersion = 'version'
kLabels = 'labels'
kLabelName = 'name'
kLabelId = 'id'
kLabelAliases = 'aliases'
kLabelCreated = 'created'
kLabelModified = 'modified'


logging.basicConfig(level=logging.INFO)  # for test


def labels_file_name() -> str:
    return 'labels.yaml'


def labels_file_path(mir_root: str) -> str:
    file_dir = os.path.join(mir_root, '.mir')
    os.makedirs(file_dir, exist_ok=True)
    return os.path.join(file_dir, labels_file_name())


class LabelFileHandler:
    # csv file: type_id, reserve, main_label, alias_label_1, xxx
    def __init__(self, mir_root: str) -> None:
        self._label_file = labels_file_path(mir_root=mir_root)

        # create if not exists
        label_file = Path(self._label_file)
        label_file.touch(exist_ok=True)

    def get_label_file_path(self) -> str:
        return self._label_file

    def _write_label_file(self, all_labels: List[dict]) -> None:
        """
        dump all label content into a label storage file, old file contents will be lost
        Args:
            all_labels (List[dict]): all labels, for each element: id, name, aliases, created, modified
        """
        obj = {kVersion: EXPECTED_FILE_VERSION, kLabels: all_labels}
        with open(self._label_file, 'w') as f:
            yaml.safe_dump(obj, f)

    def get_all_labels(self) -> List[dict]:
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
        # if empty file, returns default list
        if not obj:
            return []

        version = obj.get(kVersion, 0)
        if version != EXPECTED_FILE_VERSION:
            raise ValueError(f"version mismatch: expected: {EXPECTED_FILE_VERSION} != actual: {version}")

        labels: List[dict] = obj.get(kLabels, [])
        result_labels: List[dict] = []

        label_names_set: Set[str] = set()  # use to check dumplicate label names
        for label in labels:
            # use stripped lower case for each label
            label_name = label[kLabelName].strip().lower()
            label_aliases = [v.strip().lower() for v in label.get(kLabelAliases, [])]

            # check label name dumplicate and inline dumplicate
            if label_name in label_names_set:
                raise ValueError(f"dumplicated label name: {label_name}")
            name_and_aliases = label_aliases + [label_name]
            if len(name_and_aliases) != len(set(name_and_aliases)):
                raise ValueError(f"dumplicated inline label: {name_and_aliases}")

            # construct result
            label[kLabelName] = label_name
            if label_aliases:
                label[kLabelAliases] = label_aliases

            result_labels.append(label)
            label_names_set.add(label_name)

        return result_labels

    def merge_labels(self, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
        logging.info(f"wants to merge: {candidate_labels}")  # for test
        # check `candidate_labels` has no duplicate
        candidate_labels_list = [x.lower().split(",") for x in candidate_labels]
        candidates_list = [x for row in candidate_labels_list for x in row]
        if len(candidates_list) != len(set(candidates_list)):
            logging.info(f"conflict candidate labels: {candidate_labels_list}")
            return candidate_labels_list

        current_timestamp = time.time()

        # all labels in storage file, for each element: id, name, aliases (optional), created, modified
        existed_labels = self.get_all_labels()
        # key: label name, value: idx
        existed_main_names_to_ids: Dict[str, int] = {label[kLabelName]: idx for idx, label in enumerate(existed_labels)}

        # for main names in `existed_main_names_to_ids`, update alias
        # for new main names, add them to `candidate_labels_list_new`
        candidate_labels_list_new: List[List[str]] = []
        for candidate_list in candidate_labels_list:
            main_name = candidate_list[0]
            if main_name in existed_main_names_to_ids:  # update alias
                idx = existed_main_names_to_ids[main_name]
                # update `existed_labels`
                label = existed_labels[idx]
                label[kLabelName] = candidate_list[0]
                label[kLabelAliases] = candidate_list[1:]
                label[kLabelModified] = current_timestamp
            else:  # new main_names
                candidate_labels_list_new.append(candidate_list)

        # check dumplicate for `existed_labels_list`
        existed_labels_list = []
        for label in existed_labels:
            existed_labels_list.append(label[kLabelName])
            existed_labels_list.extend(label.get(kLabelAliases, []))
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
            logging.info(f"candidate set: {candidate_set}")  # for test
            logging.info(f"existed labels set: {existed_labels_set}")  # for test
            if set.intersection(candidate_set, existed_labels_set):  # at least one label exist.
                conflict_labels.append(candidate_list)
                continue

            existed_labels.append({
                kLabelId: len(existed_labels),
                kLabelName: candidate_list[0],
                kLabelAliases: candidate_list[1:],
                kLabelCreated: current_timestamp,
                kLabelModified: current_timestamp,
            })
            logging.info(f"candidate list added: {candidate_list}")  # for test
            logging.info(f"existed labels 175: {existed_labels}")
            existed_labels_set.update(candidate_set)
        logging.info(f"conflict labels: {conflict_labels}")

        if not (check_only or conflict_labels):
            self._write_label_file(existed_labels)
        return conflict_labels
        pass

    def get_main_labels_by_ids(self, type_ids: Iterable) -> List[str]:
        with open(self._label_file, newline='') as f:
            reader = csv.reader(f)
            all_main_names = [one_row[2] for one_row in reader]

        main_names = []
        for type_id in type_ids:
            type_id = int(type_id)
            if type_id >= len(all_main_names):
                raise ValueError(f"get_main_labels_by_ids input type_ids error: {type_ids}")
            else:
                main_names.append(all_main_names[type_id])

        return main_names
