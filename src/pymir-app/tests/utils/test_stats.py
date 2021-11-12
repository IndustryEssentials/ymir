import random
import time

import pytest

from app.utils import stats as m


@pytest.fixture(scope="function")
def redis_stats_obj(mocker):
    return m.RedisStats("redis://redis:6379/0", [])


class TestRedisStats:
    user_id = "0233"

    def test_update_task_stats(self, redis_stats_obj, mocker):
        task_type = random.randint(1, 6)
        redis_stats_obj.update_counter = fake_counter = mocker.Mock()
        redis_stats_obj.stats_group = [task_type]

        redis_stats_obj.update_task_stats(self.user_id, task_type)
        fake_counter.assert_called_with(
            redis_stats_obj.conn,
            "stats:0233:task",
            str(task_type),
            tz=redis_stats_obj.tz,
        )

    def test_get_task_stats(self, redis_stats_obj, mocker):
        redis_stats_obj.get_counter = mocker.Mock(return_value=[])
        assert not redis_stats_obj.get_task_stats(
            self.user_id, random.choice(m.PRECISION)
        )

        counts = [
            (int(time.time()), random.randint(1, 6)),
            (int(time.time()), random.randint(1, 6)),
            (int(time.time()), random.randint(1, 6)),
        ]
        counts.sort()
        redis_stats_obj.get_counter = mocker.Mock(return_value=counts)
        redis_stats_obj.stats_group = list(range(5))
        assert redis_stats_obj.get_task_stats(self.user_id, random.choice(m.PRECISION))

    def test_update_model_rank(self, redis_stats_obj, mocker):
        redis_stats_obj._update_rank = mock_update = mocker.Mock()
        model_id = random.randint(100, 200)
        redis_stats_obj.update_model_rank(self.user_id, model_id)
        mock_update.assert_called_with(
            redis_stats_obj.conn,
            f"{redis_stats_obj.prefix}:{self.user_id}:model",
            str(model_id),
        )

    def test_get_top_models(self, redis_stats_obj, mocker):
        redis_stats_obj._get_rank = mock_rank = mocker.Mock(return_value=[])
        assert not redis_stats_obj.get_top_models(self.user_id)
        ranks = [
            (random.randint(1, 6), random.randint(1, 6)),
            (random.randint(1, 6), random.randint(1, 6)),
            (random.randint(1, 6), random.randint(1, 6)),
        ]
        redis_stats_obj._get_rank = mock_rank = mocker.Mock(return_value=ranks)
        assert redis_stats_obj.get_top_models(self.user_id) == ranks

    def test_update_dataset_rank(self, redis_stats_obj, mocker):
        redis_stats_obj._update_rank = mock_update = mocker.Mock()
        dataset_id = random.randint(100, 200)
        redis_stats_obj.update_dataset_rank(self.user_id, dataset_id)
        mock_update.assert_called_with(
            redis_stats_obj.conn,
            f"{redis_stats_obj.prefix}:{self.user_id}:dataset",
            str(dataset_id),
        )

    def test_get_top_datasets(self, redis_stats_obj, mocker):
        redis_stats_obj._get_rank = mock_rank = mocker.Mock(return_value=[])
        assert not redis_stats_obj.get_top_datasets(self.user_id)
        ranks = [
            (random.randint(1, 6), random.randint(1, 6)),
            (random.randint(1, 6), random.randint(1, 6)),
            (random.randint(1, 6), random.randint(1, 6)),
        ]
        redis_stats_obj._get_rank = mock_rank = mocker.Mock(return_value=ranks)
        assert redis_stats_obj.get_top_datasets(self.user_id) == ranks

    def test_update_counter(self, redis_stats_obj, mocker):
        pipe = mocker.Mock()
        gen_pipe = mocker.Mock(return_value=pipe)
        conn = mocker.Mock(pipeline=gen_pipe)
        redis_stats_obj.update_counter(conn, "prefix", "name", redis_stats_obj.tz)
        assert pipe.zadd.call_count == pipe.hincrby.call_count == len(m.PRECISION)

    def test_get_counter(self, redis_stats_obj, mocker):
        counts = dict(
            [
                (int(time.time()), random.randint(1, 6)),
                (int(time.time()) + 10, random.randint(1, 6)),
                (int(time.time()) + 20, random.randint(1, 6)),
            ]
        )
        conn = mocker.Mock()
        conn.hgetall.return_value = counts
        expected = list(counts.items())
        expected.sort()

        assert (
            redis_stats_obj.get_counter(
                conn, "prefix", "name", random.choice(m.PRECISION)
            )
            == expected
        )
