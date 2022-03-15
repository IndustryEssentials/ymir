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
    for _, label_info in user_labels.items():
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
    for _, label_info in user_labels.items():
        names += [label_info["name"]] + label_info["aliases"]
    new_names = [name for label in new_labels for name in label.split(",")]

    return list(set(names) & set(new_names))


def convert_keywords_to_classes(user_labels: Dict, keywords: List[str]) -> List[int]:
    return [user_labels[keyword]["id"] for keyword in keywords]


def convert_classes_to_keywords(user_labels: Dict, classes: List) -> List[str]:
    id_to_labes = dict()
    for _, label_info in user_labels.items():
        id_to_labes[label_info["id"]] = label_info
    return [id_to_labes[class_id]["name"] for class_id in classes]
