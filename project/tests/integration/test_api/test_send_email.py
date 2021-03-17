from unittest import mock

import botocore.session
from botocore.stub import Stubber
from django.conf import settings

import project.apps.api.tasks
from project.apps.api.tasks import send_email


def test_send_email(monkeypatch):
    email = "user@example.com"

    monkeypatch.setattr(settings, "AWS_SES_EMAIL_SOURCE", email)
    monkeypatch.setattr(settings, "AWS_SES_REGION", "default")

    ses_client = botocore.session.get_session().create_client(
        "ses", region_name=settings.AWS_SES_REGION
    )
    stubber = Stubber(ses_client)

    def client_mock(a, **kwargs):
        return ses_client

    boto3_mock = mock.Mock()
    boto3_mock.client = client_mock
    monkeypatch.setattr(project.apps.api.tasks, "boto3", boto3_mock)

    expected_response = {"MessageId": "12345"}

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

    stubber.add_response("send_email", expected_response, expected_args)
    stubber.activate()

    send_email((email,), subject=subject, body=body)
