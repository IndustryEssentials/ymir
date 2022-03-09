import csv
import logging
import os
from collections import Counter
from pathlib import Path
import time
from typing import List, Iterable

from controller.config import label_task as label_task_config


EXPECTED_FILE_VERSION = 1


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

    def _write_label_file(self, content: List[List[str]]) -> None:
        """
        This function is used to dump all label content into a label storage file, old file contents will be lost
        Args:
            content (List[List[str]]): ALL content to be written, list of row of strings
                id, main name, aliases, ...
        """
        with open(self._label_file, "w", newline='') as f:
            writer = csv.writer(f)
            for idx, row in enumerate(content):
                row.insert(0, str(idx))
                row.insert(1, "")
                writer.writerow(row)

    def get_all_labels(self, with_reserve: bool = True, with_id: bool = True) -> List[List[str]]:
        """
        get all labels from labels.csv

        Args:
            with_reserve (bool): if true, returns preserve arg in each line
            with_id: if true, returns type id (as str) in each line

        Returns:
            all labels, one element for each line
            type_id (if with_id), preserved (if with_reserve), main name, alias...
        """
        all_labels, expected_id, = [], 0
        labels_set, labels_cnt = set(), 0
        with open(self._label_file, newline='') as f:
            reader = csv.reader(f)
            for record in reader:
                cur_labels = [label.lower() for label in record]
                assert len(cur_labels) >= 3

                # update and check unique count
                labels_cnt += len(cur_labels) - 2  # remove id and preserve field
                labels_set.update(cur_labels[2:])
                assert labels_cnt == len(labels_set)  # no duplicate inline

                # check ids.
                cur_id = int(cur_labels[0])
                assert cur_id == expected_id
                expected_id += 1

                if not with_reserve:
                    cur_labels.pop(label_task_config.LABEL_RESERVE_COLUMN)
                if not with_id:
                    cur_labels.pop(0)
                all_labels.append(cur_labels)

        return all_labels

    def merge_labels(self, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
        # check `candidate_labels` has no duplicate
        candidate_labels_list = [x.lower().split(",") for x in candidate_labels]
        candidates_list = [x for row in candidate_labels_list for x in row]
        if len(candidates_list) != len(set(candidates_list)):
            logging.info(f"conflict candidate labels: {candidate_labels_list}")
            return candidate_labels_list

        # [main name, alias 1, alias 2, ...]
        existed_labels_without_id = self.get_all_labels(with_reserve=False, with_id=False)
        # key: main name, value: index
        existed_main_names_to_ids = {row[0]: idx for idx, row in enumerate(existed_labels_without_id)}

        # for main names in `existed_main_names_to_ids`, update alias
        # for new main names, add them to `candidate_labels_list_new`
        candidate_labels_list_new = []
        for candidate_list in candidate_labels_list:
            main_name = candidate_list[0]
            if main_name in existed_main_names_to_ids:  # update alias
                idx = existed_main_names_to_ids[main_name]
                existed_labels_without_id[idx] = candidate_list
            else:  # new main_names
                candidate_labels_list_new.append(candidate_list)

        # get 
        existed_labels_list = [x for row in existed_labels_without_id for x in row]
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

            existed_labels_without_id.append(candidate_list)
            existed_labels_set.update(candidate_set)
        logging.info(f"conflict labels: {conflict_labels}")

        if not (check_only or conflict_labels):
            self._write_label_file(existed_labels_without_id)
        return conflict_labels

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
