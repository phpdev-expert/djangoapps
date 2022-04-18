from django.db import models
from model_utils.models import TimeStampedModel


class Category(TimeStampedModel):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = "category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
