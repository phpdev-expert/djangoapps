from django.db import models
from model_utils.models import TimeStampedModel


class EmailRecipient(TimeStampedModel):
    email = models.EmailField()

    class Meta:
        app_label = "email"
        verbose_name_plural = "Recipient(s)"

    def __str__(self):
        return self.email
