import json
import itertools
from operator import attrgetter
from typing import List, Iterator, Dict

from pydantic import BaseModel


def groupby(items: List, key: str) -> itertools.groupby:
    key_ = attrgetter(key)
    return itertools.groupby(sorted(items, key=key_), key=key_)


def split_seq(sequence: List, batch_size: int = 5) -> Iterator:
    """Split an iterable into smaller sublists"""
    seq = iter(sequence)
    while True:
        sublist = list(itertools.islice(seq, batch_size))
        if sublist:
            yield sublist
        if len(sublist) < batch_size:
            break


def dump_to_json(data_model: BaseModel) -> Dict:
    return json.loads(data_model.json())


def exclude_nones(data: Dict) -> Dict:
    # explicitly convert any IntEnum to Int
    data = json.loads(json.dumps(data))
    res = {}
    for k, v in data.items():
        if v is not None:
            res[k] = v
    return res
