import os
from controller.utils.labels import LabelFileHandler


class TestLabelFileHandler:
    def remove_label_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_merge(self):
        self.remove_label_file("./labels.csv")

        label_handler = LabelFileHandler("./")

        candidate_labels = ["a,aa,aaa", "h,hh,hhh", "z"]
        label_handler.merge_labels(candidate_labels)
        res = label_handler.get_all_labels(with_reserve=False)
        assert res == [["0", "a", "aa", "aaa"], ["1", "h", "hh", "hhh"], ["2", "z"]]

        candidate_labels = ["a,aa,aaa", "m,hh", "zz"]
        label_handler.merge_labels(candidate_labels)
        res = label_handler.get_all_labels(with_reserve=False)

        assert res == [["0", "a", "aa", "aaa"], ["1", "h", "hh", "hhh"], ["2", "z"]]

        candidate_labels = ["a,aa", "h", "xx,xxx"]
        label_handler.merge_labels(candidate_labels)
        res = label_handler.get_all_labels(with_reserve=False)

        assert res == [["0", "a", "aa"], ["1", "h"], ["2", "z"], ["3", "xx", "xxx"]]

        self.remove_label_file("./labels.csv")
