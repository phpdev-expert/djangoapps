from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from webapp.apps.api.serializers.metrics import MetricsAnalyticsPostSerializer
from webapp.apps.metrics.models import Post
from webapp.base.base_api import BaseAPIView
from webapp.base.constants import POST_METRIC_FORMAT
from webapp.base.utils import generate_metric_value


class CreateViewSetMixin(mixins.CreateModelMixin, GenericViewSet):
    """
    A viewset that provides default `create()` actions.
    """


class CommonPostTableViewSetMixin(BaseAPIView, CreateViewSetMixin):
    queryset = Post.objects.all()
    serializer_class = MetricsAnalyticsPostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.data

        posts = self.get_queryset().filter(
            page__page_id__in=request_data.get("page_urn"),
            # post_date__gte=request_data.get('start'),
            # post_date__lte=request_data.get('end'),
        )
        output = []
        for post in posts:
            post_id = post.post_id
            tmp = {
                "urn": post_id,
                "name": post.title,
                "text": "",
                "post_date": post.post_date,
                **generate_metric_value(post, POST_METRIC_FORMAT, request_data),
            }
            output.append(tmp)

        return Response(output)
