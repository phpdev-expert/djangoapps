from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.utils.exceptions import InvalidSerializer
from recruit_api.apps.core.user.serializers import ChangePasswordSerializer


class PasswordOperations(RecruitOperations):
    def __init__(self, user):
        self.user = user

    def update(self, data):
        serializer = ChangePasswordSerializer(data=data)
        if serializer.is_valid():
            return serializer.update(self.user, serializer.data)
        raise InvalidSerializer("Unable to validate Serializer: ChangePassword", serializer.errors)
