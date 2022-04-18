from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import (api_view, permission_classes, authentication_classes)
from rest_framework.permissions import IsAuthenticated

from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.utils.api.auth import RecruitAuthentication
from recruit_api.apps.core.user.operations import PasswordOperations


@api_view(['POST'])
@authentication_classes([RecruitAuthentication])
@permission_classes((IsAuthenticated,))
def change_password(request):
    try:
        PasswordOperations(request.user).update(request.data)
        data = ResponseData()
        data.message = "Password has been updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
    except (Exception, AuthenticationFailed) as ex:
        return RecruitResponse.get_exception_response(ex)
