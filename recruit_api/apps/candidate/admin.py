from django.contrib import admin
from recruit_api.apps.candidate.models import Candidate
from recruit_api.apps.candidate.models.candidate import ThirdParty
from recruit_api.apps.candidate.models.candidate import UsersLog
from reversion.admin import VersionAdmin

class CandidateAdmin(VersionAdmin):
    Queries = []
    list_display = ('id', 'name')
    # fields = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    list_per_page = 20


admin.site.register(Candidate, CandidateAdmin)


class ThirdPartyAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(ThirdParty, ThirdPartyAdmin)


class UsersLogAdmin(admin.ModelAdmin):
    list_display = ['log']

admin.site.register(UsersLog, UsersLogAdmin)
