from rest_framework import serializers
from recruit_api.apps.email.models import EmailRecipient
from django.core.validators import EmailValidator


class EmailRecipientSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailRecipient
        exclude = ('created', 'modified')


class SendEmailRecipientSerializer(serializers.Serializer):
    subject = serializers.CharField(read_only=True, allow_blank=False)
    recipients = serializers.EmailField(validators=[EmailValidator])
    # file = serializers.FileField(allow_empty_file=True, allow_null=True)
