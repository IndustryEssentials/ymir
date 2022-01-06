import random

import pytest

from app.utils import email as m
from tests.utils.utils import random_email, random_lower_string


class TestSendEmail:
    def test_send_email_not_enabled(self, mocker):
        email_to = random_email()
        s = mocker.patch.object(m, "settings")
        s.EMAILS_ENABLED = False

        with pytest.raises(AssertionError):
            m.send_email(email_to)

    def test_send_email(self, mocker):
        email_to = random_email()
        s = mocker.patch.object(m, "settings")
        s.EMAILS_ENABLED = True

        mocker.patch.object(m, "JinjaTemplate")
        msg = mocker.Mock()
        msg.send.return_value = res = mocker.Mock()
        mocker.patch.object(m.emails, "Message", return_value=msg)

        assert m.send_email(email_to) == res

    def test_send_task_result(self, mocker):
        email_to = random_email()
        task_id = random.randint(100, 200)
        task_name = random_lower_string(5)
        task_type = random_lower_string(5)
        mock_send_email = mocker.Mock()
        m.send_email = mock_send_email = mocker.Mock()

        m.send_task_result_email(email_to, task_id, task_name, task_type, mocker.Mock())
        mock_send_email.assert_called()
