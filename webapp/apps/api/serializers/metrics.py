# -*- coding: utf-8 -*-
from rest_framework import serializers
from webapp.apps.metrics.models import Metrics


class MetricsInsightSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    page = serializers.CharField(source="page.name")
    metrics = serializers.CharField(source="metrics.metric")
    end_time = serializers.DateTimeField()
    value = serializers.CharField()

    class Meta:
        fields = ("id", "page", "metric", "end_time", "value")


class MetricsGetSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    def get_attributes(self, obj):
        attributes = obj.attributes
        return attributes

    class Meta:
        model = Metrics
        fields = ("id", "slug", "name", "description", "platform", "attributes")


class MetricGetFilterSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(required=True)
    breakdown = serializers.CharField(required=False, default="page")
    object_id = serializers.CharField(required=False)
    aggregration = serializers.CharField(default="As is")
    since = serializers.DateField(required=False)
    until = serializers.DateField(required=False)
    slug = serializers.CharField(required=False)

    class Meta:
        model = Metrics
        fields = (
            "platform",
            "breakdown",
            "aggregration",
            "object_id",
            "since",
            "until",
            "slug",
        )


class MetricPostFilterSerializer(serializers.ModelSerializer):
    pageid = serializers.CharField(required=False)
    platform = serializers.CharField(required=True)
    breakdown = serializers.CharField(required=False, default="page")
    object_id = serializers.CharField(required=False)
    aggregration = serializers.CharField(default="As is")
    since = serializers.DateField(required=False)
    until = serializers.DateField(required=False)
    slug = serializers.CharField(required=False)
    name = serializers.CharField(required=True)

    class Meta:
        model = Metrics
        fields = (
            "pageid",
            "platform",
            "breakdown",
            "aggregration",
            "object_id",
            "since",
            "until",
            "slug",
            "name",
        )


# class PageMetricsDailySerializer(serializers.ModelSerializer):
#     date = serializers.DateTimeField(source='end_time')
#     class Meta:
#         model = PageMetricsDaily
#         fields = ('date', 'value')

# class FacebookPageSerializer(serializers.ModelSerializer):
#     page_urn = serializers.CharField(source="page_id")
#     class Meta:
#         model = Page
#         fields = ('page_urn', 'name', 'status')

# class FacebookPagePostSerializer(serializers.ModelSerializer):
#     page_urn = serializers.CharField(source="page_id")
#     class Meta:
#         model = Page
#         fields = ('page_urn',)


# class MetricsAnalyticsPostSerializer(serializers.ModelSerializer):
#     page_urn = serializers.ListField()
#     # start = serializers.DateField(required=False)
#     # end = serializers.DateField(required=False)

#     class Meta:
#         model = Page
#         fields = ('page_urn', ) #'start', 'end', )


# class FacebookPageVideoSerializer(serializers.ModelSerializer):
#     page_urn = serializers.SlugRelatedField(
#         queryset=Page.objects.filter(type=FACEBOOK),
#         slug_field='page_id',
#         many=True
#     )
#     start = serializers.DateField()
#     end = serializers.DateField()

#     class Meta:
#         model = Page
#         fields = ('page_urn', 'start', 'end')

# class PagePostSerializer(serializers.ModelSerializer):
#     page_urn = serializers.ListField()
#     start = serializers.DateField(required=False)
#     end = serializers.DateField(required=False)

#     class Meta:
#         model = Page
#         fields = ('page_urn', 'start', 'end')
