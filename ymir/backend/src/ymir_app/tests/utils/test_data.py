from app.utils import data as m


class TestGroupby:
    def test_group_by(self, mocker):
        items = [mocker.Mock(rank=r) for r in [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]]
        groups = list(m.groupby(items, "rank"))
        for i in range(4):
            assert groups[i][0] == i + 1


class TestSplitSeq:
    def test_split_seq(self, mocker):
        seq = (i for i in range(5))
        result = list(m.split_seq(seq, 2))
        assert len(result) == 3
        assert result[0] == [0, 1]
        assert result[1] == [2, 3]
        assert result[2] == [4]

        result = list(m.split_seq(range(2), 2))
        assert result == [[0, 1]]
