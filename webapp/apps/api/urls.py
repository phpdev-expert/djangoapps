
from django.conf.urls import url, include
from rest_framework import routers
from webapp.apps.api.views.views import TestApi
from webapp.apps.api.views.metrics import MetricsInsightViewSet, MetricsViewSet
from webapp.apps.api.views.facebook import FacebookPageAnalyticsViewSet, FacebookPageViewSet,\
FacebookPagePostTableViewSet, FacebookPageVideosViewSet, FacebookPagePostViewSet
from webapp.apps.api.views.instagram import InstagramPageAnalyticsViewSet, InstagramPageViewSet, \
InstagramPagePostTableViewSet
#from webapp.apps.api.views.reports import ReportsViewSet

router = routers.SimpleRouter(trailing_slash=False)
# router.register(r'reports', ReportsViewSet)

router.register(r'metrics/insights', MetricsInsightViewSet)
router.register(r'metrics', MetricsViewSet)

router.register(r'facebook/page/analytics', FacebookPageAnalyticsViewSet)
router.register(r'facebook/page/post-table', FacebookPagePostTableViewSet)
router.register(r'facebook/page/posts', FacebookPagePostViewSet)
router.register(r'facebook/page/video', FacebookPageVideosViewSet)
router.register(r'facebook/page', FacebookPageViewSet)

router.register(r'instagram/page/analytics', InstagramPageAnalyticsViewSet)
router.register(r'instagram/page/post-table', InstagramPagePostTableViewSet)
router.register(r'instagram/page/posts', FacebookPagePostViewSet)
router.register(r'instagram/page', InstagramPageViewSet)

urlpatterns = [
    #url('test/?$', TestApi.as_view(), name='test-api'),
    url(r'^', include(router.urls)),
]