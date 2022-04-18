from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.utils.exceptions import InvalidSerializer
from recruit_api.apps.core.user.models import PersonalInfo
from recruit_api.apps.core.user.serializers import (PersonalInfoSerializer, PersonalInfoGetSerializer)


class PersonalInfoOperations(RecruitOperations):

    def __init__(self, user):
        self.user = user

    def get(self, pk):
        try:
            return PersonalInfo.objects.get(pk=pk)
        except PersonalInfo.DoesNotExist:
            return None

    def get_by_user(self):
        try:
            return PersonalInfo.objects.get(user=self.user)
        except PersonalInfo.DoesNotExist:
            return None

    def get_data(self):
        personal_info = self.get_by_user()
        return PersonalInfoGetSerializer(personal_info).data

    def create_or_update(self, data):
        serializer = PersonalInfoSerializer(data=data)
        if serializer.is_valid():
            return serializer.create_or_update(self.user, data)
        raise InvalidSerializer("Unable to validate Serializer: PersonalInfo", serializer.errors)

