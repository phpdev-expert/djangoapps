from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import (api_view, permission_classes, authentication_classes)
from rest_framework.permissions import IsAuthenticated
from recruit_api.apps.utils.api.auth import RecruitAuthentication

from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.core.user.operations import PersonalInfoOperations


@api_view(['GET', 'POST'])
@authentication_classes([RecruitAuthentication])
@permission_classes((IsAuthenticated,))
def personal_info(request):
    try:
        data = ResponseData()
        po = PersonalInfoOperations(request.user)

        if request.method == 'POST':
            po.create_or_update(request.data)
            data.message = "User Personal Info has been updated successfully."
            return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

        elif request.method == 'GET':
            data.message = "User Personal Info has been fetched successfully."
            data.result = po.get_data()
            return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    except (Exception, AuthenticationFailed) as ex:
        return RecruitResponse.get_exception_response(ex)
