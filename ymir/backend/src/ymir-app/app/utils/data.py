import itertools
import json
from operator import attrgetter
from typing import Dict, List, Optional


def groupby(items: List, key: str) -> itertools.groupby:
    key_ = attrgetter(key)
    return itertools.groupby(sorted(items, key=key_), key=key_)


def parse_optional_json(j: Optional[str]) -> Dict:
    return json.loads(j) if j is not None else {}
