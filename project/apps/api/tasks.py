import logging

import boto3
from botocore.exceptions import ClientError
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_email(recepients, subject, body):
    """Sends email to given recepients via AWS Simple Email Service."""
    logger.info(
        "Sending email:\n" "from: %s\n" "to: %s\n" "using region: %s\n",
        settings.AWS_SES_EMAIL_SOURCE,
        recepients,
        settings.AWS_SES_REGION,
    )

    ses = boto3.client("ses", region_name=settings.AWS_SES_REGION)
    try:
        response = ses.send_email(
            Source=settings.AWS_SES_EMAIL_SOURCE,
            Destination={"ToAddresses": recepients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
    except ClientError as e:
        logger.error("Error sending email: %s", e.response["Error"]["Message"])
    else:
        logger.info("Email sent: id=%s", response["MessageId"])
