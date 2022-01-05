import os
from random import randint
from unittest.mock import patch

from app.utils import scheduler as m


class TestGenCronJobs:
    def test_gen_cron_jobs(self, mocker):
        mock_cron = mocker.patch.object(m, "cron")
        interval = randint(31, 60)
        m.gen_cron_jobs(interval)
        RUN_TIMES = set(range(0, 60, interval))
        mock_cron.assert_called_with(m.update_task_status, second=RUN_TIMES)
