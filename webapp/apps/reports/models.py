from django.db import models
from django.contrib.postgres.fields import JSONField

from webapp.apps.base.models import BaseModel
from webapp.apps.metrics.models import Metrics, PAGE_TYPE

STYLE_TYPES = (
    ("line_chart", "Line Chart"),
    ("table_chart", "Table Chart"),
    ("column", "Column"),
    ("area", "Area"),
    ("simple_radial_bar_chart", "Simple Radical Bar Chart"),
)
REPORT_TYPES = (
    ("facebook", "facebook"),
    ("instagram", "instagram"),
    ("linkedin", "linkedin"),
    ("twitter", "twitter"),
    ("custom", "custom"),
)


# Reports Model
class Reports(BaseModel):
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=REPORT_TYPES)

    def __str__(self):
        return self.title


# Model to track user/page and reports mapping
class UserReportMapping(BaseModel):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    page_id = models.CharField(max_length=255, null=True, blank=True)
    report = models.ForeignKey(
        Reports,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="report_map",
    )

    class Meta:
        unique_together = ("report", "user_id", "page_id")

    def __str__(self):
        return "{} - {}".format(self.user_id, self.report)


class Widget(BaseModel):
    report = models.ForeignKey(
        Reports, on_delete=models.CASCADE, related_name="widgets"
    )
    type = models.CharField(max_length=255)
    platform = models.CharField(
        max_length=255, choices=PAGE_TYPE, null=True, blank=True
    )
    breakdown = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    aggregration = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=0)
    style = JSONField()

    class Meta:
        db_table = "report_widget"
        ordering = ("order",)

    def __str__(self):
        return self.type


class WidgetTemplate(BaseModel):
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    style_type = models.CharField(max_length=50, choices=STYLE_TYPES)

    class Meta:
        db_table = "report_widget_template"

    def __str__(self):
        return self.metrics.slug + " : " + self.style_type


class PerformanceConfig(BaseModel):
    user_id = models.CharField(max_length=20)
    platform = models.CharField(max_length=20)
    page_ids = JSONField()
    slugs = JSONField()

    class Meta:
        db_table = "report_performance_config"

    def __str__(self):
        return self.user_id + ":" + self.platform
