from django.conf.urls import include, url
from django.urls import path

from rest_framework_nested import routers
from webapp.apps.api.views.metrics_v2 import MetricsViewSet, cleanup
from webapp.apps.api.views.accounts import AccountObjectViewSet
from webapp.apps.api.views.performance import PostPerformanceViewSet
from webapp.apps.api.views.reports_v2 import ReportsViewSet, ReportWidgetViewSet
from webapp.apps.api.views.stats import StatHealthViewSet
from webapp.apps.api.views.views import SyncCompletedTimeAPI
from webapp.apps.streams.views.boards_view import BoardsViewSet
from webapp.apps.streams.views.streams_view import StreamsViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"metric", MetricsViewSet)
router.register(r"stats/health", StatHealthViewSet)
router.register(r"account/object", AccountObjectViewSet)
router.register(r"report", ReportsViewSet)
router.register(r"streamapi/board", BoardsViewSet, basename="Board")
router.register(r"streamapi/stream", StreamsViewSet, basename="Stream")

router.register(r"performance", PostPerformanceViewSet)

report_router = routers.NestedSimpleRouter(router, r"report", lookup="report")
report_router.register(r"widget", ReportWidgetViewSet, base_name="v2-report-widget")


urlpatterns = [
    path('cleanup', cleanup, name='cleanup'),
    url(r"^", include(router.urls)),
    url(r"^", include(report_router.urls)),
] + [url(r"sync/time", SyncCompletedTimeAPI.as_view(), name="sync-completion-time"),]
