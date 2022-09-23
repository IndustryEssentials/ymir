from datetime import datetime
import logging
import os

import fasteners  # type: ignore
from google.protobuf import json_format
import yaml

from mir.tools.class_ids import LabelStorage, SingleLabel, UserLabels
from proto import backend_pb2

# indirect imports so that ymir_app does not need to import mir-cmd package.
from mir.version import YMIR_VERSION  # type: ignore # noqa
from mir.tools.class_ids import ids_file_name, load_or_create_userlabels  # type: ignore # noqa


def merge_labels(label_storage_file: str,
                 new_labels: UserLabels,
                 check_only: bool = False) -> UserLabels:
    with fasteners.InterProcessLock(path=os.path.realpath(label_storage_file) + '.lock'):
        current_labels = UserLabels(storage_file=label_storage_file)
        current_time = datetime.now()

        conflict_labels = []
        for label in new_labels.labels:
            new_label = SingleLabel.parse_obj(label.dict())
            idx = current_labels.id_and_main_name_for_name(label.name)[0]

            # in case any alias is in other labels.
            conflict_alias = []
            for alias in label.aliases:
                alias_idx = current_labels.id_and_main_name_for_name(alias)[0]
                if alias_idx >= 0 and alias_idx != idx:
                    conflict_alias.append(alias)
            if conflict_alias:
                new_label.id = -1
                conflict_labels.append(new_label)
                continue

            new_label.update_time = current_time
            if idx >= 0:  # update alias.
                new_label.id = idx
                new_label.create_time = current_labels.labels[idx].create_time
                current_labels.labels[idx] = new_label
            else:  # insert new record.
                new_label.id = len(current_labels.labels)
                new_label.create_time = current_time
                current_labels.labels.append(new_label)

        if not (check_only or conflict_labels):
            label_storage = LabelStorage(labels=current_labels.labels)
            with open(label_storage_file, 'w') as f:
                yaml.safe_dump(label_storage.dict(), f)

        logging.info(f"conflict labels: {conflict_labels}")
        return UserLabels(labels=conflict_labels)


def userlabels_to_proto(user_labels: UserLabels) -> backend_pb2.LabelCollection:
    return json_format.Parse(user_labels.json(), backend_pb2.LabelCollection(), ignore_unknown_fields=False)


def parse_labels_from_proto(label_collection: backend_pb2.LabelCollection) -> UserLabels:
    label_dict = json_format.MessageToDict(label_collection,
                                           preserving_proto_field_name=True,
                                           use_integers_for_enums=True)

    return UserLabels.parse_obj(label_dict)
