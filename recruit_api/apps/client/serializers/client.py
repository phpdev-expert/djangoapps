from rest_framework import serializers
from recruit_api.apps.client.models import Client
from recruit_api.apps.client.models.client import Contact
from recruit_api.apps.job.models import Job
from recruit_api.apps.utils.serializers import ChoicesSerializerField
from recruit_api.apps.client.serializers.contactemail import ContactEmailSerializer
from recruit_api.apps.client.serializers.contactphone import ContactPhoneSerializer

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        exclude = ('created', 'modified')


class ContactListSerializer(serializers.ModelSerializer):
    status_display = ChoicesSerializerField()
    phone = ContactPhoneSerializer(read_only=True, many=True)
    email = ContactEmailSerializer(read_only=True, many=True)
    class Meta:
        model = Contact
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    status_display = ChoicesSerializerField()
    class Meta:
        model = Contact
        fields = '__all__'

class ClientListSerializer(serializers.ModelSerializer):
    contact = ContactListSerializer(read_only=True, many=True)
    job=serializers.SerializerMethodField()

    def get_job(self, client):
        return Job.objects.filter(client=client).all().values()

    class Meta:
        model = Client
        fields = ('id', 'contact','name', 'job', 'location', 'founded_year', 'website', 'employee_count', 'logo_url', 'company_info',
                  'competitors', 'selling_points', 'products', 'description', 'fee','shortname','city',
                  'state','zip','country','linkedin')
