import json

from django.conf import settings
from webapp.apps.metrics.models import Account

from webapp.apps.api.tests.platform import PlatformTester


class MetricViewTest(PlatformTester):
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

    def check_fb_post_reactions(self, sotc, roman):
        # post reaction with breakdown type
        headers = self.get_headers(sotc)
        body = {"platform": "facebook", "name": "Post Reactions", "breakdown": "type"}
        response = self.client.post("/api/v2/metric", **headers, data=json.dumps(body))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(type(data[0]["value"]), dict)
        self.assertTrue("page" not in data)

        # post reaction with breakdown post
        headers = self.get_headers(sotc)
        body = {"platform": "facebook", "name": "Post Reactions", "breakdown": "post"}
        response = self.client.post("/api/v2/metric", **headers, data=json.dumps(body))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        print("reaction data :: ", data)
        self.assertTrue("post_id" in data[0])
        self.assertTrue("social" in data[0])
        self.assertEqual(type(data[0]["social"]["Post Reactions"]), int)

        # post reaction with no breakdown
        headers = self.get_headers(roman)
        body = {"platform": "facebook", "name": "Post Reactions"}
        response = self.client.post("/api/v2/metric", **headers, data=json.dumps(body))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(type(data[0]["value"]), int)
        self.assertTrue("post_id" not in data[0])

    def test_metric_name(self):
        """
        Ensure we can get metric values for multiple conditions
        """
        sotc = self.get_platform({"user_id": 193, "page_id": "141241782704241"})
        roman = self.get_platform({"user_id": 193, "page_id": "102529741293471"})
        remit = self.get_platform({"user_id": 193, "page_id": "103373784427610"})

        self.check_common_metrics(self.get_metrics("sotc"), self.get_headers(sotc))
        self.check_common_metrics(self.get_metrics("remit"), self.get_headers(remit))

        swiggy = self.get_platform({"user_id": 193, "page_id": "17841400756533683"})
        self.check_common_metrics(self.get_metrics("swiggy"), self.get_headers(swiggy))

        pmpyxis = self.get_platform({"user_id": 193, "page_id": "1073889170320351233"})
        self.check_common_metrics(
            self.get_metrics("pmpyxis"), self.get_headers(pmpyxis)
        )

        # ensure we get data for all page if no pageid passed on headers
        body = {"name": "Fans", "platform": roman["type"]}
        self.check_data_all_pages(body, self.get_headers(roman))

        # ensure we can get data for multiple platform
        # headers["HTTP_PAGEID"] = roman["page_id"]# + "," + swiggy["page_id"]
        # platforms = "facebook"
        # response = self.client.get('/api/v2/metric/Post%20Impressions?platform={}'.format(
        #   platforms),**headers )
        # self.assertEqual(response.status_code, 200)
        # print(response.content)
        # data = json.loads(response.content)["data"]
        # self.assertEqual(len(data), 2)

        # ensure we can use slug instead of name
        headers = self.get_headers(sotc)
        body = {"name": "-", "slug": "pageCheckins", "platform": sotc["type"]}
        self.check_metric(body, headers)

        # ensure we can use daterange
        body = {
            "name": "Post Clicks",
            "platform": sotc["type"],
            "breakdown": "post",
            "since": "2020-04-20",
            "until": "2020-04-21",
        }
        data = self.check_metric(body, headers)
        self.assertTrue(len(data) > 0)

        body = {
            "name": "Post Clicks",
            "platform": sotc["type"],
            "breakdown": "post",
            "since": "2020-03-01",
            "until": "2020-03-30",
        }
        data = self.check_metric(body, headers)
        self.assertTrue(len(data) == 0)

        # test stats api
        response = self.client.get("/api/v2/stats/health", **headers)
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)["data"]
        # for d in data:
        #     if d['platform'] == "twitter" and d["page_name"] == "PmPyxis":
        #         print(d["Page Fans"])
        #         _size = d["Page Fans"] > 0
        #         self.assertEqual(_size, True)

        self.check_fb_post_reactions(sotc, roman)

    def test_performance_config(self):
        """
        Ensure we can create performance config and get them
        """
        # load data for all pages
        roman = self.get_platform({"user_id": 193, "page_id": "103373784427610"})

        headers = self.get_headers(roman)
        body = {
            "page_ids": ["103373784427610", "102731209764407"],
            "platform": "facebook",
            "slugs": ["pageCheckins", "postImpressions"],
        }
        response = self.client.post(
            "/api/v2/performance", **headers, data=json.dumps(body)
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)["data"]
        self.assertEqual(data, body)

        response = self.client.get(
            "/api/v2/performance?platform={}".format("facebook"), **headers
        )
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data, body)
