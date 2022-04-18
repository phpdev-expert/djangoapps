from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.job.operations import JobOperations
from rest_framework import generics
from rest_framework import viewsets
from recruit_api.apps.job.models import *
from recruit_api.apps.job.serializers import JobSerializer
from django.db.models import Q
from recruit_api.apps.job.models import Job
from recruit_api.apps.job.models.job import Skills
from recruit_api.apps.job.operations.jobemail import JobEmailOperations
from recruit_api.apps.job.operations.jobphone import JobPhoneOperations
from recruit_api.apps.job.operations.jobtitle import JobTitleOperations

from rest_framework.views import APIView
from recruit_api.apps.job.serializers import VisaListSerializer
from rest_framework.response import Response
from django.shortcuts import render,redirect,get_object_or_404
from recruit_api.apps.candidate.models.candidate import ThirdParty
from rest_framework import generics
from recruit_api.apps.job.models.job import VisaStatusRates

class VisaStatusAPIView(APIView):
    serializer_class = VisaListSerializer
    def get(self,request):
        allstatus=VisaStatusRates.objects.all()
        serializer=VisaListSerializer(allstatus,many=True)
        return Response(serializer.data)

    def post(self,request):
        data = ResponseData()
        serializer=VisaListSerializer(data=request.data);
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VisaStatusDetail(APIView):
    """
    Retrieve, update or delete a person instance.
    """

    def get_object(self, pk):
        try:
            return VisaStatusRates.objects.get(pk=pk)
        except VisaStatusRates.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        visa_status = self.get_object(pk)
        serializer = VisaListSerializer(visa_status)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        visa_status = self.get_object(pk)
        serializer = VisaListSerializer(visa_status, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        visa_status = self.get_object(pk)
        visa_status.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class JobView(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    def create(self, request, *args, **kwargs):
        data=request.data
        print('SKILDDDDDDDDDDDDDDDDDDDDDDDDD')
        print(data['skills'])
        newskill=""
        allskill=data['skills'].split(',')
        for sk in allskill:
            if sk.isdigit():
                newskill=newskill+str(sk)+','
            else:
                client = Skills()
                client.title=sk
                client.save()
                cid=client.pk
                newskill=newskill+str(cid)+','

        ns=newskill.rstrip(',')
        print('NEW SKILSSS   SKILDDDDDDDDDDDDDDDDDDDDDDDDD')
        print(ns)
        data['skills']=ns
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        page=self.request.query_params.get('page')
        client = self.request.query_params.get('client')
        status = self.request.query_params.get('status')
        if client:
            queryset = Job.objects.filter(client=client)
            #queryset = Job.objects.all()
        else:
            location = self.request.query_params.get('location')
            category = self.request.query_params.get('category')
            skill = self.request.query_params.get('skill')
            term = self.request.query_params.get('terms')
            salary = self.request.query_params.get('salary')
            emptype= self.request.query_params.get('emptype')
            client_drop= self.request.query_params.get('client_drop')
            prio_drop= self.request.query_params.get('prio_drop')

            if status:
                candidates=Job.objects.filter(id__gte=0,status=status)
            else:
                candidates=Job.objects.filter(id__gte=0)
            if term:
                candidates = candidates.filter(
                  Q(title__icontains=term))


            if location:
                candidates=candidates.filter(location__icontains=location)

            if category:
                category=category.split(",")
                candidates=candidates.filter(category__id__in=category)

            if client_drop:
                candidates=candidates.filter(client__id=client_drop)

            if prio_drop:
                candidates=candidates.filter(priority=prio_drop)


            if emptype:
                allemp=emptype.split(",")
                candidates=candidates.filter(employment_type__in=allemp)

            if salary:
                allemp=salary.split(",")
                minsl=allemp[0]
                maxsl=allemp[1]
                candidates=candidates.filter(min_salary__range=(minsl, maxsl)).filter(max_salary__range=(minsl, maxsl))

            if skill:
                #skill=skill.split(",")
                #candidates=candidates.filter(skills__in=skill)
                candidates=candidates.filter(skills__icontains=skill)
            if page:
                page=int(page)
                endp=page*16
                startp=endp-16
                candidates=candidates[startp:endp]

            queryset = candidates.all()
        return queryset
