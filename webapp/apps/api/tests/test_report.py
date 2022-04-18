import json

from django.conf import settings
from webapp.apps.base.tests import BaseTestAPI
from webapp.apps.metrics.models import Account


class ReportViewTest(BaseTestAPI):
    _dir = settings.BASE_DIR.rsplit("/", 1)[0]
    fixtures = (
        "fixtures/account.json",
        "fixtures/metrics.json",
        "fixtures/metric_attr.json",
        "fixtures/ac_object.json",
        "fixtures/ac_metrics.json",
    )

    def setUp(self):
        # self.set_user()
        self.token_data = {
            193: "eyJhbGciOiJIUzI1NiJ9.eyJpZCI6MTkzfQ.2dJwJWIkYbRji-kBhfBo23QVJOTikIUn1p4e-YRKyzk"
        }

    def get_platform(self, data):
        account = Account.objects.get(user_id=data["user_id"], page_id=data["page_id"])
        return {
            "token": self.token_data.get(data["user_id"]),
            "page_id": account.page_id,
            "user_id": account.user_id,
            "type": account.type,
            "name": account.name,
        }

    def test_report(self):
        """
        Ensure we can create, get and delete reports
        """
        # test reports
        sotc = self.get_platform({"user_id": 193, "page_id": "141241782704241"})
        headers = self.get_headers(sotc)
        body = {"title": "test fb report", "platform": "facebook"}
        response = self.client.post("/api/v2/report", **headers, data=json.dumps(body))
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)["data"]
        self.assertTrue("id" in data)

        response = self.client.delete("/api/v2/report/{}".format(data["id"]), **headers)
        self.assertEqual(response.status_code, 200)
