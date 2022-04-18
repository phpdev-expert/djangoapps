from django.db import transaction
from recruit_api.apps.email.models import EmailRecipient
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.email.serializers import EmailRecipientSerializer
from recruit_api.apps.utils.exceptions import InvalidSerializer


class EmailRecipientOperations(RecruitOperations):

    def __init__(self):
        self.recipient = None

    def get(self, pk):
        if not self.recipient or self.recipient.pk != pk:
            self.recipient = EmailRecipient.objects.get(pk=pk)
        return self.recipient

    def create_or_update(self, data):
        try:
            serializer = EmailRecipientSerializer(data=data)
            if serializer.is_valid():
                _id = data.get("id", None)
                if _id:
                    recipient = self.get(_id)
                    return serializer.update(recipient, serializer.validated_data)
                return serializer.save()
            raise InvalidSerializer("Unable to validate Serializer: EmailRecipient", serializer.errors)
        except Exception as ex:
            raise ex

    def create_or_update_multiple(self, recipients):
        try:
            with transaction.atomic():
                if type(recipients) == str:
                    recipients = [recipients]
                _recipients = []
                for recipient in recipients:
                    if type(recipient) == str:
                        recipient = {'email': recipient}
                    _recipient = self.create_or_update(recipient)
                    _recipients.append(_recipient.pk)
                return _recipients
        except Exception as ex:
            raise ex
