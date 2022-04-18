from rest_framework import serializers
from recruit_api.apps.job.models import Job
from recruit_api.apps.job.models.job import Skills, HiringManager,HiringManagerTitle, HiringManagerEmail, HiringManagerPhone
from recruit_api.apps.job.models.job import VisaStatusRates
from recruit_api.apps.candidate.models import Candidate



class HiringManagerTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringManagerTitle
        exclude = ('created', 'modified')

class HiringManagerEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringManagerEmail
        exclude = ('created', 'modified')

class HiringManagerPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringManagerPhone
        exclude = ('created', 'modified')


class HiringManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = HiringManager
        fields = '__all__'


class HiringManagerListSerializer(serializers.ModelSerializer):
    phone = HiringManagerPhoneSerializer(read_only=True, many=True)
    email = HiringManagerEmailSerializer(read_only=True, many=True)
    title = HiringManagerTitleSerializer(read_only=True, many=True)
    class Meta:
        model = HiringManager
        fields = '__all__'


class JobskillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skills
        exclude = ('created', 'modified')

class JobSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    skill_name = serializers.SerializerMethodField()
    candidates= serializers.SerializerMethodField()
    hiringmanager = HiringManagerListSerializer(read_only=True, many=True)
    def get_client_name(self, job):
        return job.client.name

    def get_category_name(self, job):
        return job.category.title

    def get_skill_name(self, job):
        if job.skills:
            skl=job.skills.split(',')
            return Skills.objects.filter(id__in=skl).values()
        else:
            return []
        return job.category.title

    def get_candidates(self, job):
        return Candidate.objects.filter(job=job).count()



    class Meta:
        model = Job
        fields = '__all__'



class VisaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaStatusRates
        fields = '__all__'

class JobListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    visa_1099_bill_rate  = serializers.SerializerMethodField()
    third_party_bill_rate  = serializers.SerializerMethodField()
    green_card_bill_rate  = serializers.SerializerMethodField()
    citizen_bill_rate  = serializers.SerializerMethodField()
    hiringmanager = HiringManagerListSerializer(read_only=True, many=True)

    def get_client_name(self, job):
        return job.client.name


    def get_visa_1099_bill_rate(self, job):
        return VisaStatusRates.objects.get(id=1).visa_1099_bill_rate

    def get_green_card_bill_rate(self, job):
        return VisaStatusRates.objects.get(id=1).green_card_bill_rate

    def get_third_party_bill_rate(self, job):
        return VisaStatusRates.objects.get(id=1).third_party_bill_rate

    def get_citizen_bill_rate(self, job):
        return VisaStatusRates.objects.get(id=1).citizen_bill_rate

    class Meta:
        model = Job
        fields = ("id", "employment_type", "status", "title", "min_salary", "max_salary", "skills",
                  "short_description", "long_description", "publish_at", "publish_until", "short_description_public",
                  "employment_type_public", "annual_pay_public", "long_description_public", "location_public", "client",
                  "client_name", "category","hides" , "intake_call", "candidate_feedback", "companies_hiring", "template_email",
                  "third_party_bill_rate", "visa_1099_bill_rate","green_card_bill_rate","hiringmanager","citizen_bill_rate","recruiter","created","modified")
