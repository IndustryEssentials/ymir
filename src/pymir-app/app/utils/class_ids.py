import csv
import io
from typing import Dict, Iterator, List, Optional, Callable

from app.schemas import Keyword
from app.utils.ymir_controller import (
    ControllerClient,
    ControllerRequest,
    ExtraRequestType,
)


def keywords_to_labels(keywords: List[Keyword]) -> Iterator[str]:
    """
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    label: dog,puppy,pup,canine
    """
    for keyword in keywords:
        label = list(keyword.aliases or [])
        label.insert(0, keyword.name)  # primary_name, followed by aliases
        yield ",".join(label)


def labels_to_keywords(
    labels: List[str], filter_f: Optional[Callable] = None, offset: int = 1
) -> Iterator[Keyword]:
    """
    label: 0,dog,puppy,pup,canine
    keyword: {"name": "dog", "aliases": ["puppy", "pup", "canine"]}
    """
    for label in labels:
        partition = label.split(",")
        keyword = {"name": partition[offset], "aliases": partition[offset + 1 :]}
        if filter_f is None or filter_f(keyword):
            yield Keyword(**keyword)


def extract_names_from_keyword(keyword: Keyword) -> Iterator[str]:
    yield keyword.name
    if keyword.aliases:
        yield from keyword.aliases


def extract_names_from_labels(labels: List[str]) -> Iterator[str]:
    for keyword in labels_to_keywords(labels):
        yield from extract_names_from_keyword(keyword)


def find_duplication_in_labels(labels: List[str], new_labels: List[str]) -> List[str]:
    names = set(extract_names_from_labels(labels))
    new_names = set(new_labels)
    return list(names & new_names)


def get_keyword_id_to_name_mapping(labels: List[str]) -> Dict:
    mapping = {}
    for label in labels:
        partition = label.split(",")
        idx, primary_name = int(partition[0]), partition[1]
        mapping[idx] = primary_name
    return mapping


def get_keyword_name_to_id_mapping(labels: List[str]) -> Dict:
    mapping = {}
    for label in labels:
        partition = label.split(",")
        idx, primary_name = int(partition[0]), partition[1]
        mapping[primary_name] = idx
    return mapping


def flatten_labels(labels: List[str]) -> List[str]:
    """
    labels from controller has no leading index,
    just split it as csv to get all the names
    """
    return [name for label in list(labels) for name in label.split(",")]
