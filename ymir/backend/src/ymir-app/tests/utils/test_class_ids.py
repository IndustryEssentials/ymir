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
        assert (
            m.find_duplication_in_labels(
                ["1,cat,kitty", "2,dog,puppy"],
                ["cat"],
            )
            == ["cat"]
        )

        assert (
            m.find_duplication_in_labels(
                ["1,cat,kitty", "2,dog,puppy"],
                ["girl", "boy"],
            )
            == []
        )
