import pytest
from typing import Any
from app.utils import err as m


def test_retry(mocker: Any) -> None:
    f_raise = mocker.Mock(side_effect=ValueError)
    with pytest.raises(ValueError):
        m.retry(f_raise, n_times=3)
    assert f_raise.call_count == 3
