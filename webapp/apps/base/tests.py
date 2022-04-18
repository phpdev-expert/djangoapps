# flake8: noqa
# from rest_framework.test import APITestCase
from django.test import TestCase
from webapp.apps.metrics.models import (
    Metrics,
    Account,
    AccountMetrics,
    MetricsAttribute,
)


class BaseTestAPI(TestCase):
    token = None

    def get_headers(self, platform):
        return {
            "content_type": "application/json",
            "HTTP_TOKEN": platform["token"],
            "accept": "application/json",
            "HTTP_PAGEID": str(platform["page_id"]),
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def reset_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
