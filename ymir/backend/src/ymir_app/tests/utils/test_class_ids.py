from app.utils import class_ids as m
from common_utils.labels import UserLabels
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


class TestFindDuplicateLabels:
    def test_find_duplication_in_labels(self):
        user_labels = UserLabels.parse_obj(dict(labels=[
            {
                "name": "cat",
                "aliases": ["kitty"],
                "create_time": 1647075200.0,
                "update_time": 1647075200.0,
                "id": 0,
            },
            {
                "id": 1,
                "name": "dog",
                "aliases": ["puppy"],
                "create_time": 1647076200.0,
                "update_time": 1647076400.0,
            },
        ]))

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
