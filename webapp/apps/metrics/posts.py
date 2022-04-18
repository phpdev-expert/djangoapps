import json
from .metrics import get_graph_api, prepare_metrics

class PostMetrics():

    """
    "shareCount": 0,
    "clickCount": 3,
    "engagement": 0.107142857142857,
    "likeCount": 0,
    "impressionCount": 28,
    "commentCount": 0
    """
    @staticmethod
    def get_post_table(post_id, page_id):
        batch = [
            {
                "method":"GET",
                "relative_url": '/{}/insights?metric=["{}", "{}", "{}", "{}"]'.format(
                    post_id,
                    "post_impressions",
                    "post_engaged_users",
                    "post_clicks",
                    "post_reactions_like_total"
                    )
            },
            {
                "method":"GET",
                "relative_url": '/{}/comments'.format(post_id)
            },
            {
                "method": "GET",
                "relative_url": "/{}/sharedposts".format(post_id)
            }

        ]
        batch_response = get_graph_api(page_id).put_object(
            parent_object="/", connection_name="", batch=json.dumps(batch)
        )
        extracted_metrics = {}
        metrics = prepare_metrics(batch_response[0], extracted_metrics)
        extracted_metrics.update(metrics)

        comments = batch_response[1]
        comments = json.loads(comments["body"])["data"]
          
        shares = batch_response[1]
        shares = json.loads(shares["body"])["data"]

        extracted_metrics["commentCount"] = {'lifetime': [{'value': len(comments)}]}
        extracted_metrics["shareCount"] = {'lifetime': [{'value': len(shares)}]}

        return extracted_metrics