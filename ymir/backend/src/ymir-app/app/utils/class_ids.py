from datetime import datetime
from typing import Callable, Dict, Iterator, List, Optional

from app.schemas import Keyword


def keywords_to_labels(keywords: List[Keyword]) -> Iterator[str]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    label: dog,puppy,pup,canine
    """
    for keyword in keywords:
        label = list(keyword.aliases or [])
        label.insert(0, keyword.name)  # primary_name, followed by aliases
        yield ",".join(label)


def labels_to_keywords(user_labels: Dict, filter_f: Optional[Callable] = None) -> Iterator[Keyword]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    """

    for _, label_info in user_labels["id_to_name"].items():
        create_time = datetime.utcfromtimestamp(label_info["create_time"])
        update_time = datetime.utcfromtimestamp(label_info["update_time"])

        keyword = {
            "name": label_info["name"],
            "aliases": label_info["aliases"],
            "create_time": create_time,
            "update_time": update_time,
        }
        if filter_f is None or filter_f(keyword):
            yield Keyword(**keyword)


def find_duplication_in_labels(user_labels: Dict, new_labels: List[str]) -> List[str]:

    names = []
    for _, label_info in user_labels["id_to_name"].items():
        names += [label_info["name"]] + label_info["aliases"]

    new_names = [name for label in new_labels for name in label.split(",")]

    return list(set(names) & set(new_names))


def convert_keywords_to_classes(user_labels: Dict, keywords: List[str]) -> List[int]:
    return [user_labels["name_to_id"][keyword]["id"] for keyword in keywords]
