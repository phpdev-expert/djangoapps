from rest_framework import status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.core.user.operations import UserOperations
from recruit_api.apps.core.user.serializers import UserSerializer
from recruit_api.apps.core.user.models import User
from rest_framework import generics
from rest_framework import viewsets
@api_view(['GET'])
def user(request):
    try:
        data = ResponseData()
        data.result = UserOperations().get_as_select_list(detail_required=False)
        data.message = "User list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
    except Exception as ex:
        return RecruitResponse.get_exception_response(ex)
