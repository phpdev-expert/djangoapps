from rest_framework import serializers
from recruit_api.apps.email.models import Email


class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Email
        exclude = ('created', 'modified')
