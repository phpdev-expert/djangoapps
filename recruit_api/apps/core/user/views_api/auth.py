from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.core.user.operations import PersonalInfoOperations


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                data = ResponseData()

                data.result = {
                    'token': token.key,
                    'user_id': user.id,
                    'email': user.email,
                    'first_name': '',
                    'last_name': ''
                }

                personal_info = PersonalInfoOperations(user).get_by_user()
                if personal_info:
                    data.result['first_name'] = personal_info.first_name
                    data.result['last_name'] = personal_info.last_name

                return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
            return RecruitResponse.get_invalid_serializer_response(serializer.errors)
        except Exception as ex:
            return RecruitResponse.get_exception_response(ex)


authenticate_user = AuthToken.as_view()
