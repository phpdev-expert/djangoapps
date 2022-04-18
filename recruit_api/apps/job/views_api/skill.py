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
from recruit_api.apps.job.models import Job
from recruit_api.apps.job.models.job import Skills

class SkillView(viewsets.ModelViewSet):
    serializer_class = JobskillSerializer
    queryset = Skills.objects.all()
