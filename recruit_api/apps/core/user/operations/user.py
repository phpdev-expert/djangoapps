from recruit_api.apps.core.user.models import User
from recruit_api.apps.core.user.serializers import UserListSerializer
from recruit_api.apps.utils.operations import (RecruitOperations, SelectFieldOperations)
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)


class UserOperations(RecruitOperations):

    def __init__(self, request=None, user=None):
        self.request = request
        self.user = request.user if request else user

    def get(self, pk):
        return User.objects.get(pk=pk)

    def get_as_select_list(self, detail_required=True, none_required=True):
        users = User.objects.all()
        _users = []
        if none_required:
            none = SelectFieldOperations().get_none_option()
            if detail_required:
                none['detail'] = {}
            _users.append(none)
        for user in users:
            _user = {
                SELECT_FIELD_SERIALIZER_VALUE: user.id,
                SELECT_FIELD_SERIALIZER_LABEL: user.username
            }
            if detail_required:
                _user['detail'] = UserListSerializer(user, many=False).data
            _users.append(_user)
        return _users
