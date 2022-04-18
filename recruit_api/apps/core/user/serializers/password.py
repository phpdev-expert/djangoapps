from rest_framework import serializers
from recruit_api.apps.utils.exceptions import RecruitException


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, min_length=5)
    password = serializers.CharField(required=True, min_length=5)
    confirm_password = serializers.CharField(required=True, min_length=5)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        old_password = validated_data.pop("old_password")
        password = validated_data.pop("password")
        confirm_password = validated_data.pop("confirm_password")
        if not instance.check_password(old_password):
            _message = "Incorrect old password."
            raise RecruitException(_message, {'old_password': [_message]})
        if password != confirm_password:
            _message = "Password Mismatch."
            raise RecruitException(_message, {'confirm_password': [_message]})
        if password == old_password:
            _message = "Your new password is the same as old."
            raise RecruitException(_message, {'password': [_message]})
        instance.set_password(password)
        instance.save()
