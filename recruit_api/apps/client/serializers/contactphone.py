from rest_framework import serializers
from recruit_api.apps.client.models.client import ContactPhone


class ContactPhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactPhone
        exclude = ('created', 'modified')
