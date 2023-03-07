import pytest

from auth.utils import email as m
from tests.utils.utils import random_email


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
