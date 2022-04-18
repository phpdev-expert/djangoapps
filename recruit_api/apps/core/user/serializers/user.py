from rest_framework import serializers
from recruit_api.apps.core.user.models import User
from recruit_api.apps.utils.exceptions import RecruitException


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('created', 'modified', "user_permissions","is_superuser","is_staff","groups","last_login")

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        confirm_password = validated_data.pop("confirm_password", None)
        if password != confirm_password:
            raise RecruitException("Password Mismatch.", {
                'confirm_password': ['Password Mismatch.']
            })
        return User.objects.create_user(email, password, **validated_data)


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('created', 'modified', "password")
