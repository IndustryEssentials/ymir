import os
from google.protobuf import json_format

from mir.tools.class_ids import LabelStorage, SingleLabel, UserLabels  # noqa
from proto import backend_pb2

# indirect imports so that ymir_app does not need to import mir-cmd package.
from mir.tools.class_ids import ids_file_name, load_or_create_userlabels  # type: ignore # noqa


def userlabels_to_proto(user_labels: UserLabels) -> backend_pb2.LabelCollection:
    return json_format.Parse(user_labels.json(), backend_pb2.LabelCollection(), ignore_unknown_fields=False)


def parse_labels_from_proto(label_collection: backend_pb2.LabelCollection) -> UserLabels:
    label_dict = json_format.MessageToDict(label_collection,
                                           preserving_proto_field_name=True,
                                           use_integers_for_enums=True)

    return UserLabels.parse_obj(label_dict)


def user_label_file(sandbox_root: str, user_id: str) -> str:
    return os.path.join(sandbox_root, user_id, ids_file_name())
