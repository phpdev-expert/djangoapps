from webapp.apps.linkedin.serializers.response_serializers.page_analytics_by_day_serializer import \
    PageAnalyticsByDayResponse, FilterPageAnalytics
from webapp.apps.linkedin.serializers.response_serializers.page_serializer import PageSerializer, PageListSerializer
from webapp.apps.linkedin.serializers.response_serializers.post_serializer import PostSerializer, \
    PostAnalyticSerializer, PostTableSerializer
from itertools import chain


class Account:
    user = None
    page = None

    def __init__(self, user, page=None):
        self.user = user
        self.page = page

    def get_page(self, filter):
        if filter.get("start") and filter.get("end"):
            instance = self.page.pagestatsbyday_set.filter(stats_date__gte=filter.get("start"), stats_date__lte=filter.get("end"))
            serializer = PageAnalyticsByDayResponse(instance, many=True)
        else:
            serializer = PageSerializer(self.page.pagestats_set.get())
        return serializer.data

    def get_page_list(self, pages):
        serializer = PageListSerializer(pages, many=True)
        return serializer.data

    def get_page_analytics_list(self, filter):
        if filter:
            serializer = FilterPageAnalytics(self.page, many=True)
        else:
            serializer = PageSerializer(self.page, many=True)
        return serializer.data
    
    def get_post_table(self):
        table = list()
        queryset = list()
        for page in self.page:
            queryset.append(page.poststats_set.all())

        serializer = PostTableSerializer(chain.from_iterable(queryset), many=True)
        sort = sorted(serializer.data, key=lambda x: x["post_date"], reverse=True)
        return sort

    def get_page_posts(self):
        posts = self.page.poststats_set.all()
        serializer = PostSerializer(posts, many=True)
        return serializer.data

    def get_page_posts_analytics(self, post_id):
        try:
            post = self.page.poststats_set.filter(urn=f"urn:li:share:{post_id}").get()
        except Exception:
            raise Exception("Post not found")
        serializer = PostAnalyticSerializer(post)
        return serializer.data
