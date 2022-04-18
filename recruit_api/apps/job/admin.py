from django.contrib import admin
from recruit_api.apps.job.models import Job
from recruit_api.apps.job.models.job import Skills
from recruit_api.apps.job.models.job import VisaStatusRates



class JobAdmin(admin.ModelAdmin):
    Queries = []
    list_display = ('id', 'title', 'client', 'category',  'employment_type', 'salary', 'status',
                    'publish_at_formatted')
    ordering = ('id', 'title', 'client', 'category',  'employment_type', 'status')
    search_fields = ('id', 'title', 'client__name', 'category__title',  'employment_type', 'status')
    list_per_page = 20

    def publish_at_formatted(self, job):
        return job.publish_at_formatted
    publish_at_formatted.short_description = "Publish At"


admin.site.register(Job, JobAdmin)
admin.site.register(Skills)
admin.site.register(VisaStatusRates)
