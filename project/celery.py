import logging

from celery import Celery

app = Celery("project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

logger = logging.getLogger(__name__)


@app.task(bind=True)
def debug_task(self):
    logger.debug("Request: %s", self.request)
