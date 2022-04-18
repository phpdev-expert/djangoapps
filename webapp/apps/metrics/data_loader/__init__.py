from facebook import GraphAPI
from django.conf import settings
from datetime import datetime
from webapp.apps.linkedin import GraphAPIError
from webapp.base.exceptions import EmptyData
from webapp.apps.metrics.models import Account, Metrics
import tweepy
import time
# from webapp.apps.linkedin import GraphAPI as LiGraphAPI
import math
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import json
import requests

api_version = getattr(settings, "FACEBOOK_API_VERSION", None)


class InputDataLoader:
    class Meta:
        abstract = True

    flag = True

    @staticmethod
    def checkIfPostBeyonTime(data):
        for item in data:
            if "timestamp" in item:
                if datetime.strptime(item["timestamp"].split("T",1)[0],"%Y-%m-%d") < datetime.strptime(settings.SYNC_SINCE,"%Y-%m-%d"):
                    return True
            elif "created_time" in item:
                if datetime.strptime(item["created_time"].split("T",1)[0],"%Y-%m-%d") < datetime.strptime(settings.SYNC_SINCE,"%Y-%m-%d"):
                    return True
        return False

    def get_page(self, page_id, user_id):
        try:
            return Account.objects.get(user_id=user_id, page_id=page_id)
        except:  # noqa E501
            return None

    def get_metrics(self, type):
        metrics = Metrics.objects.filter(platform=type).all()
        metric_ids = {}
        for m in metrics:
            metric_ids[m.metric] = m.id
        return metric_ids

    def get_graph_api(self, user_id, page_id):
        page = Account.objects.filter(user_id=user_id, page_id=page_id)
        if not page:
            raise EmptyData("No Page Token Available..")
        page = page.first()
        # if page.type == "facebook":
        graph_api = GraphAPI(access_token=page.token, version=api_version)
        # elif page.type == "instagram":
        #     graph_api = LiGraphAPI(access_token=page.token)
        # print("asds", graph_api.get_connections("17841415203417539", "media"))
        return graph_api

    def get_data(self,user_id, page_id, url, api_limit):
        graph_api = self.get_graph_api(user_id, page_id)
        batch = [{"method": "GET", "relative_url": url + f"&limit={api_limit}"}]
        batch_response = graph_api.put_object(
            parent_object="/", connection_name="", batch=json.dumps(batch)
        )
        return batch_response[0]

    def fetch_bulk_data(self, user_id, page_id, batch):

        sub_batch = []
        count = 1
        if len(batch) > 50:
            count = math.ceil(len(batch) / 50)
        for sub_batch_count in range(count):
            sub_batch.append(batch[sub_batch_count::count])
        output=[]
        for item in sub_batch:
            batch_response = self.get_graph_api(
                user_id=user_id, page_id=page_id
            ).put_object(parent_object="/", connection_name="", batch=json.dumps(item))

            for response in batch_response:
                body = json.loads(response["body"])
                if "error" in body.keys():
                    raise GraphAPIError(body)
                output += body["data"]
                # if "paging" in body:
                #     _next = body["paging"].get("next", False)
                #     if _next:
                #         relative_url = _next.replace('https://graph.facebook.com/v3.2/','')
                #         uu = list(urlparse(relative_url))
                #         qs = parse_qs(uu[4], keep_blank_values=True)
                #         del (qs['access_token'])
                #         uu[4] = urlencode(qs, doseq=True)
                #         relative_url = urlunparse(uu)
                #         paginations.append(
                #             {
                #                 "method": "GET",
                #                 "relative_url": relative_url,
                #             }
                #         )

        # if paginations:
        #     self.fetch_bulk_data(user_id, page_id, paginations, output)

        return output


    def fetch_graph_data(self, user_id, page_id, url, api_limit=25):
        # if "media_url" in url:
        #     api_limit = 150
        session = requests.Session()
        #graph_api = self.get_graph_api(user_id, page_id)
        #batch = [{"method": "GET", "relative_url": url + f"&limit={api_limit}"}]
        output = []
        #batch_response = graph_api.put_object(
        #    parent_object="/", connection_name="", batch=json.dumps(batch)
        #)
        response = self.get_data(user_id, page_id, url, api_limit) #batch_response[0]
        # print(response)
        body = json.loads(response["body"])
        if "error" in body.keys():
            if body["error"]["code"] == 2:
                time.sleep(20)
                return self.fetch_graph_data(user_id, page_id, url)
            elif body["error"]["code"] == 1:
                if api_limit > 10:
                    api_limit = api_limit - 10
                    return self.fetch_graph_data(user_id, page_id, url, api_limit)
                elif api_limit > 1:
                    print("api_limit",api_limit)
                    api_limit = api_limit - 1
                    return self.fetch_graph_data(user_id, page_id, url, api_limit)
                elif api_limit == 1:
                    api_limit = api_limit - 1
                    return self.fetch_graph_data(user_id, page_id, url, 1)
                else:
                    raise GraphAPIError(body)
            else:
                raise GraphAPIError(body)
        #print(body.keys())
        #print(body)
        output = body["data"]
        # print(body.keys())
        while "paging" in body:
            #print("paging")
            # print(body.keys())
            _next = body["paging"].get("next", False)
            if not _next:
                break
            if InputDataLoader.checkIfPostBeyonTime(body["data"]):
                break
            next_url = body["paging"]["next"]
            ## repeat 5 times until we get success response
            ## repeat with different api limit if response fails to load becuase of high limit
            retry_count = 0
            retry_with_limit = False
            while (retry_count < 6 or retry_with_limit):
                response = session.get(next_url + f"&limit={api_limit}")
                #print(next_url)
                body = json.loads(response.content)
                if "data" in body:
                    output += body["data"]
                    break;
                elif "error" in body:
                    print("error", api_limit, body)
                    if body["error"]["code"] == 2:
                        retry_with_limit = False
                        time.sleep(20*retry_count)
                    elif body["error"]["code"] == 1:
                        if api_limit > 10:
                            api_limit = api_limit - 10
                            retry_with_limit = True
                        elif api_limit > 1:
                            api_limit = api_limit - 1
                            retry_with_limit = True
                        else:
                            retry_with_limit = False
                else:
                    break;
                retry_count +=1
        return output

    def prepare_metrics(self, data, extracted_metrics):
        for datum in data:
            name = datum["name"]
            period = datum["period"]
            if period not in ["day", "lifetime"]:
                continue
            if name not in extracted_metrics:
                extracted_metrics[name] = {}
            if period not in extracted_metrics[name]:
                extracted_metrics[name][period] = datum["values"]
            else:
                extracted_metrics[name][period] += datum["values"]
        return extracted_metrics

    def connect_twitter_api(self, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(settings.TWITTER_APP_ID, settings.TWITTER_APP_SECRET)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api
