from django.db import transaction
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.candidate.serializers import (CandidateSerializer, CandidateListSerializer)
from recruit_api.apps.candidate.serializers import CandidateSerializer
from recruit_api.apps.client.serializers import ContactSerializer
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.utils.exceptions import InvalidSerializer
from recruit_api.apps.job.operations.jobemail import JobEmailOperations
from recruit_api.apps.job.operations.jobphone import JobPhoneOperations
from recruit_api.apps.job.operations.jobtitle import JobTitleOperations
from django.db.models import Q
from recruit_api.apps.fee_management.models import Fee
from recruit_api.apps.candidate.constants import (CANDIDATE_STATUS_CHOICES, DEFAULT_CANDIDATE_STATUS,
                                                  VISA_STATUS_CHOICES, DEFAULT_VISA_STATUS)
from recruit_api.apps.candidate.models.candidate import ThirdParty
from recruit_api.apps.job.models.job import Job
from recruit_api.apps.core.user.models import User
from recruit_api.apps.client.models.client import Contact
from recruit_api.apps.client.models.client import Client
from recruit_api.apps.job.models.job import  HiringManager,HiringManagerTitle, HiringManagerEmail, HiringManagerPhone
from recruit_api.apps.job.serializers.job import HiringManagerSerializer
class HiringManagerOperations(RecruitOperations):

    def __init__(self):
        self.candidate = None
        self.third_party = None

    def get(self, pk):
        if not self.candidate or self.candidate.pk != pk:
            self.candidate = HiringManager.objects.get(pk=pk)
        return self.candidate


    def create_or_update(self, data):
        try:
            with transaction.atomic():
                data['email'] = JobEmailOperations().create_or_update_multiple(data.get('email', []))
                data['phone'] = JobPhoneOperations().create_or_update_multiple(data.get('phone', []))
                data['title'] = JobTitleOperations().create_or_update_multiple(data.get('title', []))
                cid=data.get('jobid')
                serializer = HiringManagerSerializer(data=data)
                if serializer.is_valid():
                    _id = data.get('id', None)
                    if _id:
                        candidate = self.get(_id)
                        return serializer.update(candidate, serializer.validated_data)
                    hiringmanager=serializer.save()
                    if cid:
                        mployee = Job.objects.get(id=cid)
                        mployee.hiringmanager.add(hiringmanager)
                    return Job.objects.get(id=cid)
                raise InvalidSerializer("Unable to validate Serializer: Job", serializer.errors)
        except Exception as ex:
            raise ex
