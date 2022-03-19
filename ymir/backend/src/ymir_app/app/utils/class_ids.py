from datetime import datetime
from typing import Callable, Iterator, List, Optional

from app.schemas import Keyword
from common_utils.labels import UserLabels


def keywords_to_labels(keywords: List[Keyword]) -> Iterator[str]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    label: dog,puppy,pup,canine
    """
    for keyword in keywords:
        label = list(keyword.aliases or [])
        label.insert(0, keyword.name)  # primary_name, followed by aliases
        yield ",".join(label)


def labels_to_keywords(user_labels: UserLabels, filter_f: Optional[Callable] = None) -> Iterator[Keyword]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    """
    for label in user_labels.labels:
        keyword = {
            "name": label.name,
            "aliases": label.aliases,
            "create_time": datetime.utcfromtimestamp(label.create_time),
            "update_time": datetime.utcfromtimestamp(label.update_time),
        }
        if filter_f is None or filter_f(keyword):
            yield Keyword(**keyword)


def find_duplication_in_labels(user_labels: UserLabels, new_labels: List[str]) -> List[str]:
    names = []
    for label in user_labels.labels:
        names += [label.name] + label.aliases
    new_names = [name for label in new_labels for name in label.split(",")]

    return list(set(names) & set(new_names))
