from typing import Callable, Dict, Iterator, List, Optional, Set

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


def labels_to_keywords(personal_labels: Dict, filter_f: Optional[Callable] = None) -> Iterator[Keyword]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    """
    for _, label_info in personal_labels["id_to_name"].items():
        keyword = {"name": label_info["name"], "aliases": label_info["aliases"]}
        if filter_f is None or filter_f(keyword):
            yield Keyword(**keyword)


def extract_names_from_labels(personal_labels: Dict) -> Set:
    all_labels = set()
    for _, label_info in personal_labels["id_to_name"].items():
        all_labels.add(label_info["name"])
        all_labels.add(label_info["aliases"])

    return all_labels


def find_duplication_in_labels(personal_labels: Dict, new_labels: List[str]) -> List[str]:
    names = extract_names_from_labels(personal_labels)
    new_names = set(flatten_labels(new_labels))
    return list(names & new_names)


def flatten_labels(labels: List[str]) -> List[str]:
    """
    labels from controller has no leading index,
    just split it as csv to get all the names
    """
    return [name for label in list(labels) for name in label.split(",")]
