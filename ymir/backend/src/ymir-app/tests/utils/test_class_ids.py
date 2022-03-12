from app.utils import class_ids as m
from tests.utils.utils import random_lower_string


def create_keyword():
    return m.Keyword(
        **{
            "name": random_lower_string(),
            "aliases": [random_lower_string(), random_lower_string()],
        }
    )


class TestKeywordsToLabels:
    def test_keywords_to_labels(self):
        keywords = [create_keyword() for i in range(3)]
        labels = list(m.keywords_to_labels(keywords))

        for i in range(3):
            assert keywords[i].name == labels[i].split(",")[0]


def test_flatten_labels():
    assert m.flatten_labels(["cat,kitty", "dog,puppy"]) == [
        "cat",
        "kitty",
        "dog",
        "puppy",
    ]


class TestFindDuplicateLabels:
    def test_find_duplication_in_labels(self):
        user_labels = {
            "id_to_name": {
                1: {
                    "name": "cat",
                    "aliases": ["kitty"],
                    "create_time": 1647075200.0,
                    "update_time": 1647075200.0,
                    "id": 1,
                },
                2: {
                    "id": 2,
                    "name": "dog",
                    "aliases": ["puppy"],
                    "create_time": 1647076200.0,
                    "update_time": 1647076400.0,
                },
            },
            "name_to_id": {
                "cat": {
                    "name": "cat",
                    "aliases": ["kitty"],
                    "create_time": 1647075200.0,
                    "update_time": 1647075200.0,
                    "id": 1,
                },
                "dog": {
                    "id": 2,
                    "name": "dog",
                    "aliases": ["puppy"],
                    "create_time": 1647076200.0,
                    "update_time": 1647076400.0,
                },
            },
        }

        assert (
            m.find_duplication_in_labels(
                user_labels,
                ["cat"],
            )
            == ["cat"]
        )

        assert (
            m.find_duplication_in_labels(
                user_labels,
                ["girl", "boy"],
            )
            == []
        )
