from rest_framework import serializers
from recruit_api.apps.candidate.models.candidate import ThirdParty


class ThirdPartySerializer(serializers.ModelSerializer):

    class Meta:
        model = ThirdParty
        fields = '__all__'
