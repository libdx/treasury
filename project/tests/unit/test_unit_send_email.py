from unittest import mock

from django.conf import settings

import project.apps.api.tasks
from project.apps.api.tasks import send_email


def test_unit_send_email(monkeypatch):
    email = "user@example.com"

    monkeypatch.setattr(settings, "AWS_SES_EMAIL_SOURCE", email)
    monkeypatch.setattr(settings, "AWS_SES_REGION", "default")

    client_mock = mock.Mock()
    client_mock.send_email = mock.MagicMock()

    def new_client_mock(a, **kwargs):
        return client_mock

    boto3_mock = mock.Mock()
    boto3_mock.client = new_client_mock
    monkeypatch.setattr(project.apps.api.tasks, "boto3", boto3_mock)

    subject = "Welcoming"
    body = "Hi There!"

    expected_args = {
        "Source": email,
        "Destination": {"ToAddresses": (email,)},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    }

    send_email((email,), subject=subject, body=body)

    client_mock.send_email.assert_called_once_with(**expected_args)
