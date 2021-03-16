import pytest

import project.apps.api.tasks
from project.apps.api.models import Attempt, Treasure


def test_attempt_verify(monkeypatch, db):
    def mock_send_email(recepients, subject, body):
        pass

    monkeypatch.setattr(project.apps.api.tasks, "send_email", mock_send_email)

    treasure = Treasure.objects.create(latitude=10, longitude=10)
    treasure.save()

    attempt = Attempt.objects.create(latitude=10, longitude=10)
    attempt.save()

    attempt.verify()

    assert attempt.treasure == treasure
    assert Attempt.objects.first().treasure == treasure
