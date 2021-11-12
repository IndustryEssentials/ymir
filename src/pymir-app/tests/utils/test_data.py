from app.utils import data as m


class TestGroupby:
    def test_group_by(self, mocker):
        items = [mocker.Mock(rank=r) for r in [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]]
        groups = list(m.groupby(items, "rank"))
        for i in range(4):
            assert groups[i][0] == i + 1
