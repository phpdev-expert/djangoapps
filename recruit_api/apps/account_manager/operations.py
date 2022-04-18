from recruit_api.apps.core.user.serializers import UserListSerializer
from recruit_api.apps.utils.operations import (RecruitOperations, SelectFieldOperations)
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)
from recruit_api.apps.account_manager.serializers import AccountManagerListSerializer
from .models import AccountManager


class AccountManagerOperations(RecruitOperations):

    def __init__(self, request=None, user=None):
        self.request = request
        self.user = request.user if request else user

    def get(self, pk):
        return AccountManager.objects.get(pk=pk)

    def get_as_select_list(self, detail_required=True, none_required=True):
        account_managers = AccountManager.objects.all()
        _account_managers = []
        if none_required:
            none = SelectFieldOperations().get_none_option()
            if detail_required:
                none['detail'] = {}
            _account_managers.append(none)
        for account_manager in account_managers:
            _user = {
                SELECT_FIELD_SERIALIZER_VALUE: account_manager.id,
                SELECT_FIELD_SERIALIZER_LABEL: account_manager.username
            }
            if detail_required:
                _user['detail'] = AccountManagerListSerializer(account_manager, many=False).data
            _account_managers.append(_user)
        return _account_managers
