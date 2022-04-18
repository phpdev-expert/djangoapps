from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.job.operations import JobOperations
from rest_framework import generics
from rest_framework import viewsets
from recruit_api.apps.job.models import *
from recruit_api.apps.job.serializers import JobskillSerializer
from django.db.models import Q
from recruit_api.apps.client.models import Client
from recruit_api.apps.client.serializers import ClientListSerializer

class ClientsView(viewsets.ModelViewSet):
    serializer_class = ClientListSerializer
    queryset = Client.objects.all()
