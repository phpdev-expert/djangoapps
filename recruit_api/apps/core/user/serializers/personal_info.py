from rest_framework import serializers
from recruit_api.apps.core.user.models import PersonalInfo


class PersonalInfoSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(required=False)

    class Meta:
        model = PersonalInfo
        fields = '__all__'

    def create_or_update(self, user, validated_data):
        try:
            validated_data.pop('email', None)
            personal_info = PersonalInfo.objects.get(user=user)
            personal_info = PersonalInfo(personal_info.id, user=user, **validated_data)
            return personal_info.save()
        except PersonalInfo.DoesNotExist:
            return PersonalInfo.objects.create(user=user, **validated_data)


class PersonalInfoGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalInfo
        fields = ('first_name', 'last_name', 'email', 'phone_number')
