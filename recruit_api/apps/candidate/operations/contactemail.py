from django.db import transaction
from recruit_api.apps.client.models.client import ContactEmail
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.client.serializers.contactemail import ContactEmailSerializer
from recruit_api.apps.utils.exceptions import InvalidSerializer


class ContactEmailOperations(RecruitOperations):

    def __init__(self):
        self.email = None

    def get(self, pk):
        if not self.email or self.email.pk != pk:
            self.email = Email.objects.get(pk=pk)
        return self.email

    def create_or_update(self, data):
        try:
            serializer = ContactEmailSerializer(data=data)
            if serializer.is_valid():
                _id = data.get("id", None)
                if _id:
                    email = self.get(_id)
                    return serializer.update(email, serializer.validated_data)
                return serializer.save()
            raise InvalidSerializer("Unable to validate Serializer: Email", serializer.errors)
        except Exception as ex:
            raise ex

    def create_or_update_multiple(self, emails):
        try:
            with transaction.atomic():
                if type(emails) == str:
                    emails = [emails]
                _emails = []
                for email in emails:
                    if type(email) == str:
                        email = {'email': email}
                    _email = self.create_or_update(email)
                    _emails.append(_email.pk)
                return _emails
        except Exception as ex:
            raise ex
