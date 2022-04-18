from django.db import models
from model_utils.models import TimeStampedModel


class Email(TimeStampedModel):
    email = models.EmailField()

    class Meta:
        app_label = "candidate"
        verbose_name_plural = 'Email(s)'

    def __str__(self):
        return self.email
