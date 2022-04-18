from django.conf.urls import url, include
from rest_framework_nested import routers

from webapp.apps.api.views.posts import RecentPostViewSet
from webapp.apps.api.views.reports import ReportsViewSet, ReportWidgetViewSet

from webapp.apps.api.views.metrics import MetricsViewSet
from webapp.apps.api.views.views import AccountList, GetPageList

router = routers.SimpleRouter(trailing_slash=False)

# router.register(r"get-report", GetReportViewSet)
router.register(r"report", ReportsViewSet)
router.register(r"metric", MetricsViewSet)
router.register(r"posts", RecentPostViewSet)

report_router = routers.NestedSimpleRouter(router, r"report", lookup="report")
report_router.register(r"widget", ReportWidgetViewSet, base_name="report-widget")


urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^", include(report_router.urls)),
] + [
    url(r"sync", GetPageList.as_view(), name="sync-account"),
    url(r"account", AccountList.as_view(), name="list-account"),
]
