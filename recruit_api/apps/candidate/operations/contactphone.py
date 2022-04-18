from django.db import transaction
from recruit_api.apps.client.models.client import ContactPhone
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.client.serializers.contactphone import ContactPhoneSerializer
from recruit_api.apps.utils.exceptions import InvalidSerializer


class ContactPhoneOperations(RecruitOperations):

    def __init__(self):
        self.phone = None

    def get(self, pk):
        if not self.phone or self.phone.pk != pk:
            self.phone = Phone.objects.get(pk=pk)
        return self.phone

    def create_or_update(self, data):
        try:
            serializer = ContactPhoneSerializer(data=data)
            if serializer.is_valid():
                _id = data.get("id", None)
                if _id:
                    phone = self.get(_id)
                    return serializer.update(phone, serializer.validated_data)
                return serializer.save()
            raise InvalidSerializer("Unable to validate Serializer: Phone", serializer.errors)
        except Exception as ex:
            raise ex

    def create_or_update_multiple(self, phones):
        try:
            with transaction.atomic():
                if type(phones) == str:
                    phones = [phones]
                _phones = []
                for phone in phones:
                    if type(phone) == str:
                        phone = {'phone': phone}
                    _phone = self.create_or_update(phone)
                    _phones.append(_phone.pk)
                return _phones
        except Exception as ex:
            raise ex
