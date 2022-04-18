from django.db import models
from model_utils.models import TimeStampedModel


class Phone(TimeStampedModel):
    phone = models.CharField(max_length=255)

    class Meta:
        app_label = "candidate"
        verbose_name_plural = 'Phone(s)'

    def __str__(self):
        return self.phone
