from rest_framework import serializers
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.core.user.models.user import User
from recruit_api.apps.utils.serializers import ChoicesSerializerField
from .email import EmailSerializer
from .phone import PhoneSerializer
from recruit_api.apps.client.serializers.client import ContactListSerializer
from recruit_api.apps.candidate.models.candidate import WeekyHours
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)
from django.db.models import Sum
from django.db.models import FloatField
from django.db.models.functions import Cast
from recruit_api.apps.job.models.job import VisaStatusRates
from recruit_api.apps.job.models import Job



class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        exclude = ('created', 'modified')

class CandidateAPIALLSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('id','created', 'modified','recruiter','send_signature_html','status')


class CandidateListSerializer(serializers.ModelSerializer):
    phone = PhoneSerializer(read_only=True, many=True)
    email = EmailSerializer(read_only=True, many=True)

    hiring_manager=serializers.SerializerMethodField()

    client_contact_name = serializers.SerializerMethodField()
    client_contact_phone = serializers.SerializerMethodField()
    client_contact_email = serializers.SerializerMethodField()
    status_display = ChoicesSerializerField()
    job_title = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    job_visa_1099_bill_rate= serializers.SerializerMethodField()
    job_third_party_bill_rate = serializers.SerializerMethodField()
    job_citizen_bill_rate= serializers.SerializerMethodField()
    job_green_card_bill_rate= serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    bill_rate_cal= serializers.SerializerMethodField()
    recruiter_name = serializers.SerializerMethodField()
    recruiter_email = serializers.SerializerMethodField()
    # rc_name = serializers.SerializerMethodField()
    am_name = serializers.SerializerMethodField()
    client_fee_percentage = serializers.SerializerMethodField()
    client_fee_amount = serializers.SerializerMethodField()
    rc_commission_percent = serializers.SerializerMethodField()
    am_commission_percent = serializers.SerializerMethodField()
    net_revenue = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    weekly_total_hours = serializers.SerializerMethodField()
    # placement_date = serializers.SerializerMethodField()
    # interview_date = serializers.SerializerMethodField()
    employment_type = serializers.SerializerMethodField()
    total_rc_commision_amount = serializers.SerializerMethodField()
    total_am_commision_amount = serializers.SerializerMethodField()
    account_manager_id = serializers.SerializerMethodField()
    third_party_id = serializers.SerializerMethodField()

    def get_job_title(self, candidate):
        if candidate.job:
            title = candidate.job.title
            return title
        else:
            return ''


    def get_job_type(self, candidate):
        if candidate.job:
            return candidate.job.employment_type if candidate.job.employment_type else ""



    def get_hiring_manager(self, candidate):
        if candidate.job:
            title = Job.objects.get(pk=candidate.job.id).hiringmanager.values()
            return title
        else:
            return ''



    def get_bill_rate_cal(self, candidate):
        if candidate.status_visa==6:
            if candidate.job:
                return VisaStatusRates.objects.get(id=1).third_party_bill_rate
            else:
                return 0
        elif candidate.status_visa==5:
            if candidate.job:
                return VisaStatusRates.objects.get(id=1).visa_1099_bill_rate
            else:
                return 0
        elif candidate.status_visa==2:
                if candidate.job:
                    return VisaStatusRates.objects.get(id=1).citizen_bill_rate

                else:
                    return 0
        elif candidate.status_visa==3:
            if candidate.job:
                return VisaStatusRates.objects.get(id=1).green_card_bill_rate
            else:
                return 0
        else:
            return 0






    def get_weekly_total_hours(self, candidate):
        return WeekyHours.objects.filter(candidate=candidate).annotate(as_float=Cast('hours', FloatField())).aggregate(Sum('as_float'))




    def get_job_citizen_bill_rate(self, candidate):
        return VisaStatusRates.objects.get(id=1).citizen_bill_rate

    def get_job_green_card_bill_rate(self, candidate):
        return VisaStatusRates.objects.get(id=1).green_card_bill_rate

    def get_job_third_party_bill_rate(self, candidate):
        return VisaStatusRates.objects.get(id=1).third_party_bill_rate



    def get_job_visa_1099_bill_rate(self, candidate):
        return VisaStatusRates.objects.get(id=1).visa_1099_bill_rate

    def get_client_name(self, candidate):
        return candidate.client.name if candidate.client else ''

    # def get_recruiter_name(self, candidate):
    #     return candidate.recruiter.username if candidate.recruiter else ''

    def get_recruiter_name(self, candidate):
        try:
            recruiter = User.objects.filter(id=candidate.send_signature_html)[0].username if candidate.send_signature_html else ""
        except:
            recruiter=''
        return recruiter

    def get_recruiter_email(self, candidate):
        try:
            recruiter = User.objects.filter(id=candidate.send_signature_html)[0].email
        except:
            recruiter=''
        return recruiter


    # def get_rc_name(self, candidate):
    #     if candidate.fee:
    #         return candidate.fee.recruiter.username
    #     else:
    #         return ''

    def get_am_name(self, candidate):
        if candidate.fee:
            if candidate.fee.account_manager:
                return candidate.fee.account_manager.username
        else:
            return ''

    def get_client_fee_percentage(self, candidate):
        if candidate.client:
            return candidate.client.fee
        else:
            return ''

    def get_client_fee_amount(self, candidate):
        if candidate.withdraw==0:
            if candidate.client:
                if candidate.client.fee:
                    if candidate.salary and candidate.fee:
                        client_fee_amount = int(candidate.client.fee)/int(100) * int(candidate.salary)
                        candidate.fee.client_fee_amount = client_fee_amount
                        return client_fee_amount
            else:
                return 0
        else:
            return 0

    def get_rc_commission_percent(self, candidate):
        if candidate.fee:
            return candidate.fee.rc_commission_percent
        else:
            return ''

    def get_am_commission_percent(self, candidate):
        if candidate.fee:
            return candidate.fee.am_commission_percent
        else:
            return ''



    def get_net_revenue(self, candidate):
        if candidate.fee:
            if candidate.fee.rc_commission_percent and candidate.fee.am_commission_percent:
                rc_commission = int(candidate.fee.rc_commission_percent)/int(100) * int(candidate.fee.client_fee_amount)
                am_commission = int(candidate.fee.am_commission_percent)/int(100) * int(candidate.fee.client_fee_amount)
                total_revenue = int(candidate.fee.client_fee_amount) - rc_commission - am_commission
                return total_revenue
            else:
                return ''
        else:
            return ''

    def get_created(self, candidate):
        created_datetime = candidate.created.strftime("%Y-%m-%d %H:%M:%S") if candidate.created else ""
        return created_datetime

    # def get_placement_date(self, candidate):
    #     placement_date = candidate.placement_date.strftime("%Y-%m-%d %H:%M:%S") if candidate.placement_date else ""
    #     return placement_date
    #
    # def get_interview_date(self, candidate):
    #     interview_date = candidate.interview_date.strftime("%Y-%m-%d %H:%M:%S") if candidate.interview_date else ""
    #     return interview_date

    def get_employment_type(self, candidate):
        if candidate.job:
            return candidate.job.employment_type if candidate.job.employment_type else ""

    def get_total_rc_commision_amount(self, candidate):
        if candidate.fee:
            total_amount = int(candidate.fee.rc_commission_percent)/int(100) * int(candidate.fee.client_fee_amount)
            return total_amount
        else:
            return ''

    def get_total_am_commision_amount(self, candidate):
        if candidate.fee:
            total_amount = int(candidate.fee.am_commission_percent) / int(100) * int(candidate.fee.client_fee_amount)
            return total_amount
        else:
            return ''

    def get_account_manager_id(self, candidate):
        if candidate.fee:
            return candidate.fee.account_manager.id if candidate.fee.account_manager else ""
        else:
            return ''

    def get_third_party_id(self, candidate):
        if candidate.third_party:
            return candidate.third_party.id if candidate.third_party else ""
        else:
            return ''

    def get_client_contact_name(self, candidate):
        clients_contact = []
        if candidate.client:
            contacts = ContactListSerializer(candidate.client.contact.all(), many=True).data
            for contact in contacts:
                updated_contacts_obj = {
                    'id': contact['id'],
                    SELECT_FIELD_SERIALIZER_VALUE: contact['name'],
                    SELECT_FIELD_SERIALIZER_LABEL: "Name"
                }
                clients_contact.append(updated_contacts_obj)
            return clients_contact if clients_contact else ""
        else:
            return ''

    def get_client_contact_phone(self, candidate):
        clients_contact = []
        if candidate.client:
            contacts = ContactListSerializer(candidate.client.contact.all(), many=True).data
            for contact in contacts:
                updated_contacts_obj = {
                    'id': contact['id'],
                    SELECT_FIELD_SERIALIZER_VALUE: contact['phone'],
                    SELECT_FIELD_SERIALIZER_LABEL: "Phone"
                }
                clients_contact.append(updated_contacts_obj)
            return clients_contact if clients_contact else ""
        else:
            return ''

    def get_client_contact_email(self, candidate):
        clients_contact = []
        if candidate.client:
            contacts = ContactListSerializer(candidate.client.contact.all(), many=True).data
            for contact in contacts:
                updated_contacts_obj = {
                    'id': contact['id'],
                    SELECT_FIELD_SERIALIZER_VALUE: contact['email'],
                    SELECT_FIELD_SERIALIZER_LABEL: "Email"
                }
                clients_contact.append(updated_contacts_obj)
            return clients_contact if clients_contact else ""
        else:
            return ''

    class Meta:
        model = Candidate
        fields = ("id", "phone", "email", "created", "name", "company", "role", "industry","modified",
                  "activity", "location", "subject", "responded", "source", "visit", "vacation", "status_visa",
                  "communication", "status", "recruiter", "job", "employment_type", "client", "linkedin_company",
                  "linkedin_role", "linkedin_industry", "linkedin_subject", "linkedin_message", "message", "notes",
                  "current_salary", "salary", "availability", "linkedin_url", "start_date", "placement_date", "interview_date",
                  "status_display", "client_fee", "job_type","job_title", "client_name", "recruiter_name","recruiter_email", "send_signature_html", "fee",
                  "am_name", "client_fee_percentage", "bill_rate_cal", "client_fee_amount", "rc_commission_percent",
                  "am_commission_percent", "net_revenue", "expected_salary", "total_am_commision_amount","total_benefits", "total_rc_commision_amount",
                  "account_manager_id", "client_contact_name", "client_contact_phone", "client_contact_email",
                  "third_party_id","follow_up","hiring_manager","resume_url","job_citizen_bill_rate","job_green_card_bill_rate", "pay_rate","job_third_party_bill_rate","job_visa_1099_bill_rate","weekly_total_hours","bill_rate_manula","bill_rate","linkedin_background","linkedin_experience1","linkedin_experience2","linkedin_experience3",
                  "linkedin_education", "linkedin_skills", "linkedin_language", "confirmed","withdraw","invoice_no","paid")
