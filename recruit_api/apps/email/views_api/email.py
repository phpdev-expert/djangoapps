from rest_framework import status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.email.operations import EmailOperations
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser


# @api_view(['POST'])
# def email(request):
#     try:
#         data = ResponseData()
#         data.result = EmailOperations().send(request.data)
#         data.message = "Email has been sent successfully."
#         return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
#     except Exception as ex:
#         return RecruitResponse.get_exception_response(ex)


class email(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, *args, **kwargs):
        try:
            data = ResponseData()
            data.result = EmailOperations().send(request.data)
            data.message = "Email has been sent successfully."
            return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
        except Exception as ex:
            return RecruitResponse.get_exception_response(ex)
