import itertools
from operator import attrgetter
from typing import List


def groupby(items: List, key: str) -> itertools.groupby:
    key_ = attrgetter(key)
    return itertools.groupby(sorted(items, key=key_), key=key_)
