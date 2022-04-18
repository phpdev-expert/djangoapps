from django.db import transaction
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.candidate.serializers import (CandidateSerializer, CandidateListSerializer)
from recruit_api.apps.candidate.serializers import CandidateSerializer
from recruit_api.apps.client.serializers import ContactSerializer
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.utils.exceptions import InvalidSerializer
from .contactemail import ContactEmailOperations
from .contactphone import ContactPhoneOperations
from django.db.models import Q
from recruit_api.apps.fee_management.models import Fee
from recruit_api.apps.candidate.constants import (CANDIDATE_STATUS_CHOICES, DEFAULT_CANDIDATE_STATUS,
                                                  VISA_STATUS_CHOICES, DEFAULT_VISA_STATUS)
from recruit_api.apps.candidate.models.candidate import ThirdParty
from recruit_api.apps.job.models.job import Job
from recruit_api.apps.core.user.models import User
from recruit_api.apps.client.models.client import Contact
from recruit_api.apps.client.models.client import Client
class ContactOperations(RecruitOperations):

    def __init__(self):
        self.candidate = None
        self.third_party = None

    def get(self, pk):
        if not self.candidate or self.candidate.pk != pk:
            self.candidate = Contact.objects.get(pk=pk)
        return self.candidate


    def create_or_update(self, data):
        try:
            with transaction.atomic():
                data['email'] = ContactEmailOperations().create_or_update_multiple(data.get('email', []))
                data['phone'] = ContactPhoneOperations().create_or_update_multiple(data.get('phone', []))
                cid=data.get('client_id')
                cname=data.get('client_name')
                if cname:
                    client = Client()
                    client.name=cname
                    client.save()
                    cid=client.pk
                serializer = ContactSerializer(data=data)
                if serializer.is_valid():
                    _id = data.get('id', None)
                    if _id:
                        candidate = self.get(_id)
                        return serializer.update(candidate, serializer.validated_data)
                    contct=serializer.save()
                    if cid:
                        mployee = Client.objects.get(id=cid)
                        mployee.contact.add(contct)
                    return contct
                raise InvalidSerializer("Unable to validate Serializer: Contact", serializer.errors)
        except Exception as ex:
            raise ex
