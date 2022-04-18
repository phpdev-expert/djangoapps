from django.db import transaction
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.candidate.serializers import (CandidateSerializer, CandidateListSerializer,CandidateAPIALLSerializer)
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.utils.exceptions import InvalidSerializer
from .email import EmailOperations
from .phone import PhoneOperations
from django.db.models import Q
from recruit_api.apps.fee_management.models import Fee
from recruit_api.apps.candidate.constants import (CANDIDATE_STATUS_CHOICES, DEFAULT_CANDIDATE_STATUS,
                                                  VISA_STATUS_CHOICES, DEFAULT_VISA_STATUS)
from recruit_api.apps.candidate.models.candidate import ThirdParty
from recruit_api.apps.job.models.job import Job
from recruit_api.apps.core.user.models import User
class CandidateOperations(RecruitOperations):

    def __init__(self):
        self.candidate = None
        self.third_party = None

    def get(self, pk):
        if not self.candidate or self.candidate.pk != pk:
            self.candidate = Candidate.objects.get(pk=pk)
        return self.candidate



    def get_recruiter_obj(self, data):
        if not 'recruiter_name' in data.keys():
            fee_obj = User.objects.filter(id=data['send_signature_html'])
            return fee_obj[0]
        fee_obj = User.objects.filter(username=data['recruiter_name'])
        return fee_obj[0]

    def create_fee_obj(self, data):
        if data['am_commission_percent'] !=''  and data['rc_commission_percent']!='' :
            fee_obj = Fee()
            fee_obj.am_commission_percent = data['am_commission_percent']
            fee_obj.rc_commission_percent = data['rc_commission_percent']
            fee_obj.account_manager_id = data['account_manager_id']
            fee_obj.save()
            return fee_obj
        else:
            fee_obj = Fee()
            fee_obj.am_commission_percent =data['am_commission_percent'] if data['am_commission_percent'] else 0
            fee_obj.rc_commission_percent = data['rc_commission_percent'] if data['rc_commission_percent'] else 0
            fee_obj.client_fee_percentage = data['client_fee_percentage'] if data['client_fee_percentage'] else 0
            fee_obj.client_fee_amount = data['client_fee_amount'] if data['client_fee_amount'] else 0
            fee_obj.account_manager_id = data['account_manager_id']
            fee_obj.save()
            return fee_obj

    def update_fee_obj(self, fee_id, data):
        if data['am_commission_percent'] !=''  and data['rc_commission_percent']!='' :
            fee_obj = Fee.objects.filter(id=fee_id)
            if fee_obj:
                fee_obj[0].am_commission_percent = data['am_commission_percent']
                fee_obj[0].rc_commission_percent = data['rc_commission_percent']
                fee_obj[0].account_manager_id = data['account_manager_id']
                fee_obj[0].save()
                return fee_obj[0]
            else:
                fee_obj = Fee()
                fee_obj.am_commission_percent = data['am_commission_percent']
                fee_obj.rc_commission_percent = data['rc_commission_percent']
                fee_obj.account_manager_id = data['account_manager_id']
                fee_obj.save()
                return fee_obj
        else:
            fee_obj = Fee()
            fee_obj.am_commission_percent =data['am_commission_percent'] if data['am_commission_percent'] else 0
            fee_obj.rc_commission_percent = data['rc_commission_percent'] if data['rc_commission_percent'] else 0
            fee_obj.client_fee_percentage = data['client_fee_percentage'] if data['client_fee_percentage'] else 0
            fee_obj.client_fee_amount = data['client_fee_amount'] if data['client_fee_amount'] else 0
            fee_obj.account_manager_id = data['account_manager_id']
            fee_obj.save()
            return fee_obj

    def create_or_update(self, data):
        try:
            with transaction.atomic():
                data['email'] = EmailOperations().create_or_update_multiple(data.get('email', []))
                data['phone'] = PhoneOperations().create_or_update_multiple(data.get('phone', []))

                if 'third_party_id' in data.keys():
                    if data['third_party_id']:
                        self.third_party = ThirdParty.objects.filter(id=data['third_party_id'])[0]

                if 'job_id' in data.keys():
                    client_id = Job.objects.filter(id=data['job_id'])[0].client.id
                    data['job'] = data['job_id']
                    data['client'] = client_id

                if 'job' in data.keys():
                    client_id = Job.objects.filter(id=data['job'])[0].client.id
                    data['job'] = data['job']
                    data['client'] = client_id

                if not 'fee' in data.keys():
                    fee_obj = self.create_fee_obj(data)
                elif 'fee' in data.keys():
                    fee_obj = self.update_fee_obj(data['fee'], data)
                recruiter_obj=self.get_recruiter_obj(data)
                data['fee'] = fee_obj.id
                data['recruiter'] = recruiter_obj.id
                serializer = CandidateSerializer(data=data)
                if serializer.is_valid():
                    _id = data.get('id', None)
                    if _id:
                        candidate = self.get(_id)
                        if self.third_party:
                            candidate.third_party = self.third_party
                        return serializer.update(candidate, serializer.validated_data)
                    return serializer.save()
                print('ERRORRRRR')
                print(serializer.errors)
                raise InvalidSerializer("Unable to validate Serializer::: Candidate", serializer.errors)
        except Exception as ex:
            raise ex

    def get_listapi(self):
        candidates = Candidate.objects.all().order_by("created")
        return CandidateAPIALLSerializer(candidates, many=True).data

    # def get_listapidash(self):
    #     candidates = Candidate.objects.all().order_by("created")
    #     return CandidateAPIDashSerializer(candidates, many=True).data

    def get_list(self,page,serch,request):
        try:
            endp=page*25
            startp=endp-25
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                if request.GET['stage_filter']!='0':
                    stages=request.GET['stage_filter'].split(',')
                    candidates=candidates.filter(status__in=stages)
                if request.GET['employe_filter']!='0':
                    candidates=candidates.filter(job__employment_type=request.GET['employe_filter'])

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])


                candidates=candidates[startp:endp]
                return CandidateListSerializer(candidates, many=True).data
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) )
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                if request.GET['stage_filter']!='0':
                    stages=request.GET['stage_filter'].split(',')
                    candidates=candidates.filter(status__in=stages)
                if request.GET['employe_filter']!='0':
                    candidates=candidates.filter(job__employment_type=request.GET['employe_filter'])

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])


                candidates=candidates[startp:endp]
                return CandidateListSerializer(candidates, many=True).data
        except Exception as ex:
            raise ex


    def get_list_total(self,page,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                if request.GET['stage_filter']!='0':
                    stages=request.GET['stage_filter'].split(',')
                    candidates=candidates.filter(status__in=stages)
                if request.GET['employe_filter']!='0':
                    candidates=candidates.filter(job__employment_type=request.GET['employe_filter'])

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])

                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) )
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                if request.GET['stage_filter']!='0':
                    stages=request.GET['stage_filter'].split(',')
                    candidates=candidates.filter(status__in=stages)
                if request.GET['employe_filter']!='0':
                    candidates=candidates.filter(job__employment_type=request.GET['employe_filter'])

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])

            return candidates.count()
        except Exception as ex:
            raise ex


    def get_list_total_sub(self,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])

                candidates=candidates.filter(status=2)
                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) ).filter(status=2).count()
            return candidates
        except Exception as ex:
            raise ex


    def get_list_total_cont(self,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                candidates=candidates.filter(status=5, job__employment_type=1)

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])
                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) ).filter(status=5, job__employment_type=1).count()
            return candidates
        except Exception as ex:
            raise ex


    def get_list_total_send(self,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                candidates=candidates.filter(status=3)

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])

                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) ).filter(status=3).count()
            return candidates
        except Exception as ex:
            raise ex


    def get_list_total_inter(self,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                candidates=candidates.filter(status=4)

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])
                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) ).filter(status=4).count()
            return candidates
        except Exception as ex:
            raise ex


    def get_list_total_perma(self,serch,request):
        try:
            if serch=='AAAALL':
                candidates = Candidate.objects.all().order_by("-modified")
                if request.GET['recruiter_filter']!='0':
                    candidates=candidates.filter(recruiter__id=request.GET['recruiter_filter'])
                if request.GET['client_filter']!='0':
                    candidates=candidates.filter(client__id=request.GET['client_filter'])
                if request.GET['job_filter']!='0':
                    candidates=candidates.filter(job__id=request.GET['job_filter'])
                candidates=candidates.filter(status=5, job__employment_type=3)

                if request.GET.get('from')!='0' and request.GET.get('to')!='0':
                    frrm=request.GET.get('from')
                    to=request.GET.get('to')
                    candidates=candidates.filter(start_date__range=[frrm,to])

                return candidates.count()
            else:
                candidates = Candidate.objects.filter(
                  Q(job__title__icontains=serch)
                | Q(client__name__icontains=serch)
                | Q(name__icontains=serch)
                | Q(current_salary__icontains=serch)
                | Q(linkedin_company__icontains=serch)
                | Q(location__icontains=serch)
                | Q(source__icontains=serch)
                | Q(salary__icontains=serch) ).filter(status=5, job__employment_type=3).count()
            return candidates
        except Exception as ex:
            raise ex


    def get_detail(self, pk):
        try:
            candidate = self.get(pk)
            return CandidateListSerializer(candidate, many=False).data
        except Exception as ex:
            raise ex
