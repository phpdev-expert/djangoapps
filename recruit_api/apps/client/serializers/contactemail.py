from rest_framework import serializers
from recruit_api.apps.client.models.client import ContactEmail

class ContactEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactEmail
        exclude = ('created', 'modified')
