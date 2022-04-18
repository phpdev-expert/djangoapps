from recruit_api.apps.utils.operations import (RecruitOperations, SelectFieldOperations)
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)
from recruit_api.apps.job.models import Job
from recruit_api.apps.job.models.job import Skills
from recruit_api.apps.category.models import Category
from recruit_api.apps.job.serializers import JobListSerializer


class JobOperations(RecruitOperations):

    def get_as_select_list(self, detail_required=True, none_required=True):
        jobs = Job.objects.all().order_by('title')
        _jobs = []
        if none_required:
            none = SelectFieldOperations().get_none_option()
            if detail_required:
                none['detail'] = {}
            _jobs.append(none)
        for job in jobs:
            _job = {
                SELECT_FIELD_SERIALIZER_VALUE: job.id,
                SELECT_FIELD_SERIALIZER_LABEL: '{} - ANEW{}'.format(job.title, job.id)
            }
            if detail_required:
                _job['detail'] = JobListSerializer(job, many=False).data
            _jobs.append(_job)
        return _jobs

    def get_as_select_list_status(self, detail_required=True, none_required=True):
        jobs=Job.objects.filter(status=1)
        _jobs = []
        if none_required:
            none = SelectFieldOperations().get_none_option()
            if detail_required:
                none['detail'] = {}
            _jobs.append(none)
        for job in jobs:
            _job = {
                SELECT_FIELD_SERIALIZER_VALUE: job.id,
                SELECT_FIELD_SERIALIZER_LABEL: '{} - ANEW{}'.format(job.title, job.id)
            }
            if detail_required:
                _job['detail'] = JobListSerializer(job, many=False).data
            _jobs.append(_job)
        return _jobs

    def get_as_category_list(self, detail_required=True, none_required=True):
        jobs = Category.objects.all()
        _jobs = []
        for job in jobs:
            _job = {
                SELECT_FIELD_SERIALIZER_VALUE: job.id,
                SELECT_FIELD_SERIALIZER_LABEL:job.title
            }
            _jobs.append(_job)
        return _jobs

    def get_as_skill_list(self, detail_required=True, none_required=True):
        jobs = Skills.objects.all()
        _jobs = []
        for job in jobs:
            _job = {
                SELECT_FIELD_SERIALIZER_VALUE: job.id,
                SELECT_FIELD_SERIALIZER_LABEL: job.title
            }
            _jobs.append(_job)
        return _jobs
