from rest_framework import serializers
from recruit_api.apps.candidate.models.candidate import WeekyHours


class  WeekyHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeekyHours
        fields = '__all__'
