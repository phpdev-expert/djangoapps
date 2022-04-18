from django.db import transaction
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.email.models import Email
from recruit_api.apps.email.serializers import EmailSerializer, SendEmailRecipientSerializer
from recruit_api.apps.utils.exceptions import InvalidSerializer
from recruit_api.apps.email.server import EmailServer
from .recipient import EmailRecipientOperations
from django.conf import settings


class EmailOperations(RecruitOperations):

    def __init__(self):
        self.email = None

    def get(self, pk):
        if not self.email or self.email.pk != pk:
            self.email = Email.objects.get(pk=pk)
        return self.email

    def create_or_update(self, data):
        try:
            with transaction.atomic():
                data['recipients'] = EmailRecipientOperations().create_or_update_multiple(data.get('recipients', []))
                serializer = EmailSerializer(data=data)
                if serializer.is_valid():
                    _id = data.get('id', None)
                    if _id:
                        email = self.get(_id)
                        return serializer.update(email, serializer.validated_data)
                    return serializer.save()
                raise InvalidSerializer("Unable to validate Serializer: Candidate", serializer.errors)
        except Exception as ex:
            raise ex

    def send(self, data):
        try:
            serializer = SendEmailRecipientSerializer(data=data)
            if serializer.is_valid():
                recipients = data['recipients']
                file = ''
                if 'file' in data.keys():
                    file = data['file']
                if type(recipients) == str:
                    recipients = [recipients]
                if EmailServer().send(data['subject'], data['message'], recipients, file):
                    data['email_from'] = settings.EMAIL_HOST_USER
                    self.create_or_update(data)
                    return True
            raise InvalidSerializer("Unable to validate Serializer: SendEmailRecipient", serializer.errors)
        except Exception as ex:
            raise ex
