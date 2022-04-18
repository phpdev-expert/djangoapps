from rest_framework import status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.client.operations import ClientOperations
from recruit_api.apps.job.operations import JobOperations


@api_view(['GET'])
def client(request):
    try:
        data = ResponseData()
        clients = ClientOperations().get_as_select_list()
        jobs = request.query_params.get('jobs', None)
        stat = request.query_params.get('status')
        if stat:
            data.result = clients if not jobs else {
                'clients': clients,
                'jobs': JobOperations().get_as_select_list_status(),
                'category': JobOperations().get_as_category_list(),
                'skills': JobOperations().get_as_skill_list(),

            }
        else:
            data.result = clients if not jobs else {
                'clients': clients,
                'jobs': JobOperations().get_as_select_list(),
                'category': JobOperations().get_as_category_list(),
                'skills': JobOperations().get_as_skill_list(),

            }
        data.message = "Client list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
    except Exception as ex:
        return RecruitResponse.get_exception_response(ex)
