from rest_framework import serializers
from recruit_api.apps.account_manager.models import AccountManager


class AccountManagerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountManager
        exclude = ('created', 'modified')