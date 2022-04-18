from django.db import models
from model_utils.models import TimeStampedModel
from recruit_api.apps.core.user.models import User
from recruit_api.apps.job.models import Job
from recruit_api.apps.client.models import Client
from recruit_api.apps.candidate.constants import (CANDIDATE_STATUS_CHOICES, DEFAULT_CANDIDATE_STATUS,
                                                  VISA_STATUS_CHOICES, DEFAULT_VISA_STATUS)
from .phone import Phone
from .email import Email
from recruit_api.apps.account_manager.models import AccountManager
from recruit_api.apps.fee_management.models import Fee
import reversion




class ThirdParty(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

@reversion.register()
class Candidate(TimeStampedModel):
    name = models.CharField(max_length=255)
    recruiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, null=True)
    third_party = models.ForeignKey(ThirdParty, on_delete=models.SET_NULL, null=True, blank=True)
    account_manager = models.ForeignKey(AccountManager, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    linkedin_company = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    linkedin_role = models.CharField(max_length=255, blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    linkedin_industry = models.CharField(max_length=255, blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    linkedin_subject = models.CharField(max_length=255, blank=True, null=True)
    responded = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    visit = models.CharField(max_length=255, blank=True, null=True)
    vacation = models.CharField(max_length=255, blank=True, null=True)
    total_benefits = models.CharField(max_length=255, blank=True, null=True)
    # visa_status = models.CharField(max_length=255, choices=VISA_STATUS_CHOICES, default=DEFAULT_VISA_STATUS)
    communication = models.CharField(max_length=255, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    current_salary = models.CharField(max_length=255, blank=True, null=True)
    expected_salary = models.CharField(max_length=255, blank=True, null=True)
    salary = models.PositiveIntegerField('Salary', blank=True, null=True)
    pay_rate = models.PositiveIntegerField('Pay Rate', blank=True, null=True)
    bill_rate = models.FloatField('Bill Rate', blank=True, null=True)
    bill_rate_manula = models.IntegerField('manula', blank=True, null=True,default=0)
    start_date = models.DateTimeField(blank=True, null=True)
    placement_date = models.DateTimeField(blank=True, null=True)
    interview_date = models.DateTimeField(blank=True, null=True)
    follow_up =  models.CharField(max_length=255, blank=True, null=True)
    phone = models.ManyToManyField(Phone, blank=True)
    email = models.ManyToManyField(Email, blank=True)
    client_fee= models.CharField(max_length=10, blank=True, null=True)
    resume_url = models.CharField(max_length=500, blank=True, null=True)
    linkedin_url = models.URLField(max_length=500, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    linkedin_message = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=CANDIDATE_STATUS_CHOICES, default=DEFAULT_CANDIDATE_STATUS)
    status_visa = models.IntegerField(choices=VISA_STATUS_CHOICES, default=DEFAULT_VISA_STATUS)
    send_signature_html = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    linkedin_background = models.TextField(blank=True, null=True)
    linkedin_experience1 = models.TextField( blank=True, null=True)
    linkedin_experience2 = models.TextField( blank=True, null=True)
    linkedin_experience3 = models.TextField( blank=True, null=True)
    linkedin_education = models.TextField(blank=True, null=True)
    linkedin_skills = models.TextField( blank=True, null=True)
    linkedin_language = models.TextField(blank=True, null=True)
    confirmed = models.IntegerField(default=0, blank=True, null=True)
    withdraw = models.IntegerField(default=0, blank=True, null=True)
    paid = models.IntegerField(default=0, blank=True, null=True)
    invoice_no = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = "candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        return self.name

class WeekyHours(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    hours = models.CharField(max_length=55, blank=True, null=True)
    client_paid = models.IntegerField(blank=True, null=True,default=0)
    candidate_paid = models.IntegerField(blank=True, null=True,default=0)
    paydate = models.DateField(blank=True, null=True)

class UsersLog(TimeStampedModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    rec = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
