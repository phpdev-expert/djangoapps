# from rest_framework import status
# from rest_framework.decorators import api_view
# from recruit_api.apps.utils.models import ResponseData
# from recruit_api.apps.utils.api.response import RecruitResponse
# from recruit_api.apps.candidate.operations import CandidateOperations
# from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
# @api_view(['GET', 'POST', 'PUT'])
# def candidate(request):
#     try:
#         data = ResponseData()
#         co = CandidateOperations()
#         if request.method == 'GET':
#             data.result = co.get_list()
#             data.message = "Candidate list has been fetched successfully."
#             return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
#         elif request.method == 'POST' or request.method == 'PUT':
#             _candidate = co.create_or_update(request.data)
#             data.result = co.get_detail(_candidate.id)
#             data.message = "Candidate has been created/updated successfully."
#             return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)
#     except Exception as ex:
#         return RecruitResponse.get_exception_response(ex)

from django.shortcuts import  get_object_or_404
from rest_framework import generics
from recruit_api.apps.candidate.models.candidate import Candidate
from recruit_api.apps.candidate.serializers.candidate import CandidateListSerializer,CandidateAPIALLSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import mixins, status
from recruit_api.apps.candidate.operations import CandidateOperations
from recruit_api.apps.candidate.operations.contact import ContactOperations
from recruit_api.apps.candidate.operations.hiringmanager import HiringManagerOperations
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.utils.models import ResponseData
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.candidate.models.candidate import UsersLog
import json
import ast
import os.path
import time



class CandidateListApiView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
         list:
         Return a list of all the existing User against some post id.

         create:
         Create a new User instance.

     """
    queryset = Candidate.objects.all()

    #permission_classes = (IsAuthenticated,)
    serializer_class = CandidateListSerializer
    name = 'candidates-list'

    def get(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        data.result = co.get_list()
        data.message = "Candidate list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def post(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        _candidate = co.create_or_update(request.data)
        data.result = co.get_detail(_candidate.id)
        data.message = "Candidate has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)

    def put(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        _candidate = co.create_or_update(request.data)
        data.result = co.get_detail(_candidate.id)
        data.message = "Candidate has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)


class CandidateListApiAllView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateAPIALLSerializer
    name = 'candidates-list-api'

    def get(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        data.result = co.get_listapi()
        print('dDDDD')
        print(request)
        data.message = "Candidate list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def post(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        _candidate = co.create_or_update(request.data)
        data.result = co.get_detail(_candidate.id)
        data.message = "Candidate has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)

    def put(self, request, *args, **kwargs):
        data = ResponseData()
        co = CandidateOperations()
        _candidate = co.create_or_update(request.data)
        data.result = co.get_detail(_candidate.id)
        data.message = "Candidate has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)


class ClientListApiView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    name = 'client-contact-list'

    def get(self, request, *args, **kwargs):
        data = ResponseData()
        co = ContactOperations()
        data.result = co.get_list()
        data.message = "Candidate list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def post(self, request, *args, **kwargs):
        data = ResponseData()
        co = ContactOperations()
        _candidate = co.create_or_update(request.data)
        data.result =request.data
        data.message = "Client has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def put(self, request, *args, **kwargs):
        data = ResponseData()
        co = ContactOperations()
        _candidate = co.create_or_update(request.data)
        data.result = request.data
        data.message = "Client has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)


class JobListApiView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    name = 'job-hiring-list'

    def get(self, request, *args, **kwargs):
        data = ResponseData()
        co = ContactOperations()
        data.result = co.get_list()
        data.message = "Candidate list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def post(self, request, *args, **kwargs):
        data = ResponseData()
        co = HiringManagerOperations()
        _candidate = co.create_or_update(request.data)
        data.result =request.data
        data.message = "Job has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def put(self, request, *args, **kwargs):
        data = ResponseData()
        co = HiringManagerOperations()
        _candidate = co.create_or_update(request.data)
        data.result = request.data
        data.message = "Job has been created/updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

class CandidateFileApiView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Candidate.objects.all()

    permission_classes = (IsAuthenticated,)
    serializer_class = CandidateListSerializer
    name = 'candidates-list-upload'


    def post(self, request, *args, **kwargs):
        data = ResponseData()
        myfile = request.FILES['file']
        extension = os.path.splitext(myfile.name)[1]
        tm=int(time.time())
        fname=str(tm)+str(extension)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(fname, myfile)
        uploaded_file_url = fs.url(filename)
        data.result = uploaded_file_url
        data.message = "File uploaded successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)


class CandidateRevApiView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Candidate.objects.all()


    serializer_class = CandidateListSerializer
    name = 'candidates-list-rev'

    def get(self, request, *args, **kwargs):
        data = ResponseData()
        logs=UsersLog.objects.all().order_by('-created').values()
        users_list = list(logs)
        data.result = users_list
        data.message = "Logs list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)

    def post(self, request, *args, **kwargs):
        data = ResponseData()
        received_json_data=json.loads(request.body)

        id = received_json_data['id']
        cadiastes=received_json_data['candidate']
        rec=received_json_data['rec']
        name=received_json_data['name']

        ulogs=  UsersLog()
        ulogs.candidate =get_object_or_404(Candidate, pk=id)
        ulogs.log = cadiastes
        ulogs.rec = rec
        ulogs.name = name
        ulogs.save()

        data.result = received_json_data['id']
        data.message = "Candidate updated successfully."
        return RecruitResponse.get_success_response(status.HTTP_201_CREATED, data)



class CandidateRetrieveAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    """
         list:
         Return a list of all the existing User against some post id.

         create:
         Create a new User instance.

     """
    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    name = 'candidates-list-retrieval'
    paginate_by = 10
    def get(self, request, *args, **kwargs):
        print('here0')
        print(request.user.id)
        data = ResponseData()
        co = CandidateOperations()
        if request.GET.get('dashboard')=='1':
            data.result = co.get_listapi()
        else:
            data.result = co.get_list(self.kwargs['page'], self.kwargs['name'],request)
        data.total = co.get_list_total(self.kwargs['page'], self.kwargs['name'],request)
        data.total_sub = co.get_list_total_sub(self.kwargs['name'],request)
        data.total_inter = co.get_list_total_inter(self.kwargs['name'],request)
        data.total_send = co.get_list_total_send(self.kwargs['name'],request)
        data.total_perma = co.get_list_total_perma(self.kwargs['name'],request)
        data.total_cont = co.get_list_total_cont(self.kwargs['name'],request)

        data.message = "Candidate list has been fetched successfully."
        return RecruitResponse.get_success_response(status.HTTP_200_OK, data)


class CandidateRetrieveUpdateDestroyAPIView(APIView):

    """
        get:
        Return a existing User instance against some comment id.

        put:
        update a existing User instance by self user.

        delete:
        delete a existing User instance by self user.

    """

    serializer_class = CandidateListSerializer
    authentication_classes = []
    permission_classes = []
    name = 'candidates-retrieve-update-delete'

    def get_object(self):
        try:
            return Candidate.objects.get(id=self.kwargs.get('pk'))
        except Candidate.DoesNotExist:
            raise NotFound

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        self.check_object_permissions(self.request, obj)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    # def delete(self, request, *args, **kwargs):
    #     obj = self.get_object()
    #     self.check_object_permissions(self.request, obj)
    #     obj.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
