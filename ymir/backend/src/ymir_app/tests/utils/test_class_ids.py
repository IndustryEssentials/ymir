from common_utils.labels import SingleLabel, UserLabels
from tests.utils.utils import random_lower_string


def create_label():
    return SingleLabel(**{
        "name": random_lower_string(),
        "aliases": [random_lower_string(), random_lower_string()],
    })


class TestFindDuplicateLabels:
    def test_find_duplication_in_labels(self):
        user_labels = UserLabels.parse_obj(
            dict(labels=[
                {
                    "name": "cat",
                    "aliases": ["kitty"],
                    "create_time": 1647075277.0,
                    "update_time": 1647075288.0,
                    "id": 0,
                },
                {
                    "id": 1,
                    "name": "dog",
                    "aliases": ["puppy"],
                    "create_time": 1647076277.0,
                    "update_time": 1647076488.0,
                },
            ]))

        assert (user_labels.find_dups(["cat"]) == ["cat"])

        assert (user_labels.find_dups(["girl", "boy"]) == [])
