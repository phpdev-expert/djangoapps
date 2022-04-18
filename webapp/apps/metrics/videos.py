import json

from webapp.apps.metrics.metrics import get_graph_api


class VideoMetrics:
    @staticmethod
    def get_video_table(video_id, page_id):
        metrics = [
            'page_video_views',
        ]

        # metrics = [
        #     'total_video_views',
        # ]

        batch = [
            {
                "method": "GET",
                "related_url": '/{}/insights?metric={}'.format(
                    video_id,
                    str(metrics)
                )
            }
        ]

        batch_response = get_graph_api(page_id).put_object(
            parent_object='/',
            connection_name='',
            batch=json.dumps(batch)
        )

        print(batch_response)