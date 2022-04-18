from django.core.validators import RegexValidator
from rest_framework import serializers

from webapp.apps.reports.models import (
    Reports,
    UserReportMapping,
    Widget,
    WidgetTemplate,
)
from webapp.apps.metrics.models import Account


class ReportSerializer(serializers.ModelSerializer):
    report_user_id = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = Reports
        fields = ("id", "title", "platform","report_user_id",)
        write_only_fields=("report_user_id",)

    def create(self, validated_data):
        try:
            auth_user_id = self.context["request"].auth_user_id
        except:
            auth_user_id = validated_data["report_user_id"]
            validated_data.pop("report_user_id")
        if validated_data["platform"] == "custom":
            page_ids = Account.objects.filter(
                user_id=auth_user_id,
                status__in = ["active", "revoked"]
            ).values_list("page_id", flat=True)
            linked_platform = Account.objects.filter(
                user_id=auth_user_id,
                status__in=["active", "revoked"]
            ).values_list("type", flat=True)
        else:
            page_ids = Account.objects.filter(
                user_id=auth_user_id,
                type=validated_data["platform"],
                status__in=["active", "revoked"]
            ).values_list("page_id", flat=True)

        if len(page_ids) == 0:
            if validated_data["platform"] == "custom":
                raise Exception(f"No accounts linked")
            else:
                raise Exception(f"No {validated_data['platform']} accounts linked")
        report_instance = Reports.objects.create(**validated_data)
        for page_id in page_ids:
            UserReportMapping.objects.get_or_create(
                user_id=auth_user_id,
                report=report_instance,
                page_id=page_id,
            )
        # create default widget
        wt = WidgetTemplate.objects.filter(metrics__platform=validated_data["platform"])
        if validated_data["platform"] == "custom":
                wt = WidgetTemplate.objects.filter(metrics__platform__in=linked_platform)
        for template in wt:
            params = dict()
            try:
                attribute = template.metrics.metricsattribute_set.first()
            except Exception:
                attribute = None
            if attribute:
                params.update({"breakdown": attribute.breakdown})
                if attribute.aggregration != "":
                    params.update({"aggregration": attribute.aggregration})
            Widget.objects.create(
                report=report_instance,
                type=template.metrics.name,
                platform=template.metrics.platform,
                style={
                    "title": template.metrics.name,
                    "type": template.style_type,
                    "size": "",
                },
                **params,
            )

        return report_instance


class UserReportMappingSerializer(serializers.ModelSerializer):
    report = ReportSerializer(many=True)

    class Meta:
        model = UserReportMapping
        fields = ("id", "user_id", "report")


class MetricValSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    date = serializers.CharField()


class WidgetStyleSerializer(serializers.Serializer):
    title = serializers.CharField()
    type = serializers.CharField()
    size = serializers.CharField()


class WidgetSerializer(serializers.Serializer):
    platform = serializers.CharField(source="report.platform")
    type = serializers.CharField()
    metric = MetricValSerializer()
    style = WidgetStyleSerializer()


class WidgetPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    type = serializers.CharField(validators=[RegexValidator(regex=r"^[()\w -:]+$")])
    style = WidgetStyleSerializer()
    breakdown = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    aggregration = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    platform = serializers.CharField()

    class Meta:
        model = Widget
        fields = ("id", "type", "style", "breakdown", "aggregration", "platform")


class WidgetPostListSerializer(serializers.Serializer):
    widgets = WidgetPostSerializer(many=True)

    class Meta:
        fields = ("widgets",)


class ReportDetailSerializer(serializers.Serializer):
    report_id = serializers.IntegerField(source="id")
    widgets = serializers.DictField()


class ReportGetRequestSerializer(serializers.Serializer):
    period = serializers.CharField(default="OVERALL")
    since = serializers.DateField(required=False)
    until = serializers.DateField(required=False)


class ReportWidgetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    platform = serializers.CharField()
    type = serializers.CharField()
    style = WidgetStyleSerializer()
    breakdown = serializers.CharField()
    aggregration = serializers.CharField()


class PerformanceConfigPostSerializer(serializers.Serializer):
    page_ids = serializers.ListField(required=True)
    platform = serializers.CharField(required=True)
    slugs = serializers.ListField(required=True)


class PerformanceConfigSerializer(serializers.Serializer):
    pass
