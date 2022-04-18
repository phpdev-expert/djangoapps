from rest_framework import serializers
from recruit_api.apps.candidate.models import Phone


class PhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Phone
        exclude = ('created', 'modified')
