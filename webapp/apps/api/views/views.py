from _datetime import datetime, timedelta
from django.utils import timezone

from rest_framework import renderers
from rest_framework.response import Response

from webapp.apps.api.serializers.accounts import SyncCompletedTimeSerializer, SyncApiSerializer
from webapp.apps.metrics.tasks.facebook import facebook_sync_task
from webapp.apps.metrics.tasks.instagram import instagram_sync_task
from webapp.apps.metrics.tasks.linkedin import linkedin_saved_task
from webapp.apps.metrics.tasks.twitter import twitter_sync_task
from webapp.apps.metrics.models import Account
from webapp.base.base_api import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

log = logging.getLogger("webapp")


class TestApi(BaseAPIView):
    """
    Test API
    """

    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request):
        auth_user_id = request.auth_user_id
        return Response("Test successful for %s" % auth_user_id)


class GetPageList(BaseAPIView):
    renderers = (renderers.JSONRenderer,)

    def _filter_queryset(self, queryset, params):
        data = {}
        if "page_id" in params:
            data.update({"page_id": params["page_id"]})
        if "type" in params:
            data.update({"type": params["type"]})
        return data

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("type", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("page_id", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("manual", openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        auth_user = request.auth_user_id

        queryset = (
            Account.objects.prefetch_related()
            .filter(status="active")
            .order_by("-date_created")
        )
        params = request.GET
        serializer = SyncApiSerializer(data=params)
        serializer.is_valid(raise_exception=True)

        manual = serializer.data.get("manual", False)
        filter = self._filter_queryset(queryset, params)
        output = queryset.filter(user_id=auth_user, **filter)
        time_threshold = datetime.now() - timedelta(hours=2)
        for page in output:
            if page.last_synced and page.last_synced.strftime("%Y-%m-%d %H:%M:%S") >= time_threshold.strftime("%Y-%m-%d %H:%M:%S") and (manual == False):
                print("if")
                continue
            print("else")
            if page.type == "facebook":
                facebook_data = {
                    "auth_user_id": page.user_id,
                    "page_id": page.page_id,
                    "status": page.status,
                }
                facebook_sync_task.delay(
                    data=facebook_data, params={"initial_sync": False}
                )
            elif page.type == "instagram":
                instagram_data = {
                    "auth_user_id": page.user_id,
                    "social_account_id": page.page_id,
                    "status": page.status,
                }
                instagram_sync_task.delay(data=instagram_data)
            elif page.type == "twitter":
                twitter_data = {
                    "social_account_id": page.page_id,
                    "access_token": page.token,
                    "access_token_secret": page.token_secret,
                    "screen_name": page.name,
                    "auth_user_id": page.user_id,
                    "status": page.status,
                }
                twitter_sync_task.delay(data=twitter_data)
            elif page.type == "linkedin":
                linkedin_data = {
                    "auth_user_id": page.user_id,
                    "page_id": page.page_id,
                    "name": page.name,
                    "access_token": page.token,
                    "status": page.status,
                    "description": page.description,
                }
                linkedin_saved_task.delay(data=linkedin_data)
        names = ", ".join(output.values_list("name", flat=True))
        return Response({"status": f"{names} are syncing."}, 200)


class AccountList(BaseAPIView):
    renderers = (renderers.JSONRenderer,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("platform", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        auth_user = request.auth_user_id

        params = request.GET
        platform = params.get("platform", None)
        queryset = (
            Account.objects.prefetch_related().exclude(data__contains={"account_type": "PERSONAL"}, type="instagram")
            .filter(user_id=auth_user, status__in=["active", "revoked"] )
            .order_by("-date_created")
        )
        if platform is not None:
            queryset = queryset.filter(type=platform)
        output = queryset.values("id", "page_id", "name", "type", "status", "data", "sync_status")
        return Response(list(output), 200)


class SyncCompletedTimeAPI(BaseAPIView):
    renderers = (renderers.JSONRenderer,)

    # @swagger_auto_schema(
    #     manual_parameters=[
    #         openapi.Parameter("platform", openapi.IN_QUERY, type=openapi.TYPE_STRING),
    #     ]
    # )
    def get(self, request):
        auth_user = request.auth_user_id
        queryset = (
                    Account.objects.prefetch_related()
                    .filter(user_id=auth_user)
                    .order_by("-date_created")
                )

        serializer = SyncCompletedTimeSerializer(queryset, many=True)
        return Response(serializer.data, 200)

