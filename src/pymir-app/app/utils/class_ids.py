import csv
import io
from typing import Dict

from ymir.ids import type_id_names


def load_type_id_names() -> Dict:
    s = io.StringIO(type_id_names.data.decode())
    reader = csv.DictReader(s, fieldnames=["id", "name"], restkey="alias")
    return {int(class_["id"]): class_["name"].strip() for class_ in reader}


CLASS_TYPES = load_type_id_names()
REVERSED_CLASS_TYPES = {v: k for k, v in CLASS_TYPES.items()}
