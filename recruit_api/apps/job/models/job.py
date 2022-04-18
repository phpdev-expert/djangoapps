from django.db import models
from django.core.validators import (MinLengthValidator, MinValueValidator)
from model_utils.models import TimeStampedModel
from recruit_api.apps.category.models import Category
from recruit_api.apps.client.models import Client
from recruit_api.apps.core.user.models import User
from recruit_api.apps.job.constants import (EMPLOYMENT_TYPE_CHOICES, DEFAULT_EMPLOYMENT_TYPE,
                                            STATUS_CHOICES, DEFAULT_STATUS, PRORITY_CHOICES, D_PRORITY_CHOICES)


class Skills(TimeStampedModel):
    title = models.CharField(max_length=255)


class HiringManagerPhone(TimeStampedModel):
    phone = models.CharField(max_length=255)

    class Meta:
        app_label = "candidate"
        verbose_name_plural = 'Phone(s)'

    def __str__(self):
        return self.phone

class HiringManagerEmail(TimeStampedModel):
    email = models.EmailField()

    class Meta:
        app_label = "candidate"
        verbose_name_plural = 'Email(s)'

    def __str__(self):
        return self.email

class HiringManagerTitle(TimeStampedModel):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = "candidate"
        verbose_name_plural = 'title(s)'

    def __str__(self):
        return self.title


class HiringManager(models.Model):
    phone = models.ManyToManyField(HiringManagerPhone, blank=True)
    email = models.ManyToManyField(HiringManagerEmail, blank=True)
    title = models.ManyToManyField(HiringManagerTitle, blank=True)


    class Meta:
        verbose_name = "HiringManager"
        verbose_name_plural = "HiringManagers"

    def __str__(self):
        return '{} - {}'.format(self.title, self.email)




class VisaStatusRates(TimeStampedModel):
    third_party_bill_rate = models.CharField(max_length=255, null=True, blank=True, default="1.18")
    visa_1099_bill_rate = models.CharField(max_length=255, null=True, blank=True, default="1.15")
    citizen_bill_rate = models.CharField(max_length=255, null=True, blank=True, default="1.18")
    green_card_bill_rate = models.CharField(max_length=255, null=True, blank=True, default="1.18")


class Job(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    employment_type = models.IntegerField(choices=EMPLOYMENT_TYPE_CHOICES, default=DEFAULT_EMPLOYMENT_TYPE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=DEFAULT_STATUS)
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=255,blank=True, null=True)
    state = models.CharField(max_length=255,blank=True, null=True)
    country = models.CharField(max_length=255,blank=True, null=True)
    skills = models.CharField(max_length=500, null=True, blank=True)
    min_salary = models.IntegerField(validators=[MinValueValidator(0)])
    max_salary = models.IntegerField(validators=[MinValueValidator(0)])
    short_description = models.CharField(max_length=150, blank=True)
    long_description = models.TextField(blank=True)
    intake_call = models.TextField(blank=True, null=True)
    hides = models.TextField(blank=True, null=True)
    candidate_feedback = models.TextField(blank=True, null=True)
    companies_hiring = models.TextField(blank=True, null=True)
    template_email = models.TextField(blank=True, null=True)
    hiringmanager = models.ManyToManyField(HiringManager, blank=True)
    notes = models.TextField(blank=True, null=True)
    publish_at = models.DateField(null=True, blank=True)
    publish_until = models.DateField(null=True, blank=True)
    short_description_public = models.BooleanField(default=True,blank=True,)
    employment_type_public = models.BooleanField(default=True)
    annual_pay_public = models.BooleanField(default=True)
    long_description_public = models.BooleanField(default=True,blank=True,)
    location_public = models.BooleanField(default=True)
    priority = models.IntegerField(choices=PRORITY_CHOICES, default=D_PRORITY_CHOICES)
    recruiter = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True, null=True)
    created=models.DateField(blank=True, null=True)
    modified=models.DateField(blank=True, null=True)

    class Meta:
        app_label = "job"
        verbose_name_plural = "Jobs"
        ordering = ['priority','-created','title']

    def __str__(self):
        return self.title

    @property
    def salary(self):
        return f'${self.min_salary}k-${self.max_salary}k'

    @property
    def publish_at_formatted(self):
        return 'N/A' if not self.publish_at else self.publish_at.strftime('%d/%m/%Y')
