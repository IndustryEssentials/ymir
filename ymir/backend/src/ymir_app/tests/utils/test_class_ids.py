from common_utils.labels import SingleLabel, UserLabels
from tests.utils.utils import random_lower_string


def create_label():
    return SingleLabel(**{
        "name": random_lower_string(),
        "aliases": [random_lower_string(), random_lower_string()],
    })


class TestKeywordsToLabels:
    def test_labels_to_csvs(self):
        labels = UserLabels.parse_obj(dict(labels=[create_label() for i in range(3)]))
        csvs = list(labels.to_csvs())

        for i in range(3):
            assert labels.labels[i].name == csvs[i].split(",")[0]


class TestFindDuplicateLabels:
    def test_find_duplication_in_labels(self):
        user_labels = UserLabels.parse_obj(
            dict(labels=[
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

        assert (user_labels.find_dups(["cat"]) == ["cat"])

        assert (user_labels.find_dups(["girl", "boy"]) == [])
