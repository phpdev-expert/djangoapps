import json
from webapp.apps.base.tests import BaseTestAPI


class PlatformTester(BaseTestAPI):
    def get_metrics(self, page_name):
        metrics = {
            "remit": [
                {"platform": "facebook", "name": "Post Organic Video Watch Duration"},
                {"platform": "facebook", "name": "Post Video Reach"},
                {"platform": "facebook", "name": "Post Video Views"},
                {"platform": "facebook", "name": "Post Video Watch Duration"},
            ],
            "sotc": [
                {"platform": "facebook", "name": "Check-ins"},
                {"platform": "facebook", "name": "Engagement", "breakdown": "type"},
                {"platform": "facebook", "name": "Engagement", "return_type": dict},
                {
                    "platform": "facebook",
                    "name": "Inbound Messages",
                    "return_type": int,
                },
                {
                    "platform": "facebook",
                    "name": "Inbound Messages Table",
                    "return_type": list,
                },
                {"platform": "facebook", "name": "Page Reactions", "return_type": int},
                {
                    "platform": "facebook",
                    "name": "Page Reactions",
                    "breakdown": "type",
                    "return_type": dict,
                },
                {"platform": "facebook", "name": "Fans"},
                {
                    "platform": "facebook",
                    "name": "Fans",
                    "breakdown": "language",
                    "return_type": dict,
                },
                {
                    "platform": "facebook",
                    "name": "Fans",
                    "breakdown": "age",
                    "return_type": dict,
                },
                {
                    "platform": "facebook",
                    "name": "Fans",
                    "breakdown": "gender",
                    "return_type": dict,
                },
                {
                    "platform": "facebook",
                    "name": "Fans",
                    "breakdown": "city",
                    "return_type": dict,
                },
                {
                    "platform": "facebook",
                    "name": "Fans",
                    "breakdown": "country",
                    "return_type": dict,
                },
                {"platform": "facebook", "name": "Negative Actions"},
                {"platform": "facebook", "name": "Page Reactions"},
                {
                    "platform": "facebook",
                    "name": "Page Reactions",
                    "breakdown": "type",
                    "return_type": dict,
                },
            ],
            "swiggy": [
                {"platform": "instagram", "name": "Reach"},
                {"platform": "instagram", "name": "Followers"},
                {"platform": "instagram", "name": "Post Impressions"},
                # Post Likes
            ],
            "pmpyxis": [
                {"platform": "twitter", "name": "Engagement"},
                {"platform": "twitter", "name": "Post Likes"},
            ],
        }
        return metrics.get(page_name)

    def get_check_metric_data(self, body, headers):
        url = "/api/v2/metric"
        response = self.client.post(url, **headers, data=json.dumps(body))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def check_metric(self, body, headers, params={"do_assert": False}):
        data = self.get_check_metric_data(body, headers)
        if params["do_assert"]:
            self.assertEqual(len(data) > 0, True)
        return data

    def check_data_all_pages(self, body, headers):
        headers.pop("HTTP_PAGEID")
        self.check_metric(body, headers)

    def check_common_metrics(self, metrics, headers):
        platform = metrics[0]["platform"]
        if platform == "facebook":
            for metric in metrics:
                with self.subTest(headers=headers, metric=metric):
                    body = metric.copy()
                    body.pop("return_type", None)
                    response = self.client.post(
                        "/api/v2/metric", **headers, data=json.dumps(body)
                    )
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.content)["data"]
                    _size = len(data) > 0
                    self.assertEqual(_size, True)
                    self.assertTrue("name" in data[0])
                    print("metric response == ", metric, "data", data)
                    if (metric.get("breakdown", None) == "type") or metric.get(
                        "breakdown", None
                    ):
                        self.assertEqual(type(data[0]["value"]), dict)
                        self.assertTrue("page_id" not in data[0])
                    else:
                        self.assertEqual(
                            type(data[0]["value"]),
                            int
                            if "return_type" not in metric
                            else metric["return_type"],
                        )
                        self.assertTrue("page" in data[0])

                    if metric["name"] == "Inbound Messages Table":
                        self.assertTrue("author" in data[0]["value"][0])

        elif platform == "instagram":
            for metric in metrics:
                with self.subTest(headers=headers, metric=metric):
                    body = metric.copy()
                    body.pop("return_type", None)
                    response = self.client.post(
                        "/api/v2/metric", **headers, data=json.dumps(body)
                    )
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.content)["data"]
                    _size = len(data) > 0
                    self.assertEqual(_size, True)
                    self.assertTrue("name" in data[0])
                    print("metric response == ", metric, "data", data)
                    # if metric.get("breakdown", None) == "type":
                    #     self.assertEqual(type(data[0]["value"]), dict)
                    #     self.assertTrue("page_id" not in data[0])
                    # else:
                    #     self.assertEqual(
                    #         type(data[0]["value"]),
                    #         int if "return_type" not in metric else metric["return_type"],
                    #     )
                    #     self.assertTrue("page" in data[0])

                    # if metric["name"] == "Inbound Messages Table":
                    #     self.assertTrue("author" in data[0]["value"][0])

        elif platform == "twitter":
            for metric in metrics:
                with self.subTest(headers=headers, metric=metric):
                    body = metric.copy()
                    body.pop("return_type", None)
                    response = self.client.post(
                        "/api/v2/metric", **headers, data=json.dumps(body)
                    )
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.content)["data"]
                    print("data::", data)
                    _size = len(data) > 0
                    self.assertEqual(_size, True)
                    self.assertTrue("name" in data[0])
        # # ensure response has data for both metrics
        # names = []
        # for d in data:
        #     name = d["name"]
        #     if name not in names:
        #         names.append(name)
        # self.assertTrue(len(names) == 2)
