import csv
from io import StringIO

from django.contrib import admin

# from django_celery_beat.admin import CrontabSchedule, PeriodicTask, PeriodicTaskAdmin
from django.http import HttpResponse

from webapp.apps.metrics.models import (
    Account,
    Metrics,
    MetricsAttribute,
    AccountMetrics,
    PostComments,
    CommentReplies,
    AccountObject,
    AccountInbox,
    TwitterReply,
    TwitterMention,
)


class CustomModelAdmin(admin.ModelAdmin):
    actions = ['download_csv']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def download_csv(self, request, queryset):
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(self.list_display)
        for s in queryset:
            row = [str(getattr(s, k)) if hasattr(s, k) else getattr(self, k)(s) for k in self.list_display]
            writer.writerow(row)
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={queryset.model.__name__}.csv'
        return response

    download_csv.short_description = "Download CSV file."


#admin.site.register(Account, admin_class=CustomModelAdmin)
# admin.site.register(AccountObject, admin_class=CustomModelAdmin)
admin.site.register(TwitterReply, admin_class=CustomModelAdmin)
admin.site.register(TwitterMention, admin_class=CustomModelAdmin)
admin.site.register(PostComments, admin_class=CustomModelAdmin)
admin.site.register(CommentReplies, admin_class=CustomModelAdmin)


@admin.register(AccountObject)
class AdminPage(CustomModelAdmin):
    """
    Account Object Admin
    """

    list_display = ["account", "object_id", "object_type", "date_posted"]
    search_fields = ["object_id", "object_type"]
    list_filter = ["account__id"]


class AccountAdmin(CustomModelAdmin):
    list_filter = ["user_id"]

admin.site.register(Account, AccountAdmin)

class MetricsAdmin(CustomModelAdmin):
    list_display = ["id", "name", "slug", "metric", "platform"]


admin.site.register(Metrics, MetricsAdmin)


class MetricsAttributeAdmin(CustomModelAdmin):
    list_display = ["id", "metrics", "breakdown", "aggregration", "ref_metric"]


admin.site.register(MetricsAttribute, MetricsAttributeAdmin)

# admin.site.register(Page)

#
# class MetricsAdmin(CustomModelAdmin):
#     list_display = ['id', 'metric', 'type']


class AccountMetricsAdmin(CustomModelAdmin):
    list_display = ["id", "account", "metrics", "object_id", "date", "value", "reply"]
    search_fields = ["account__id", "metrics__id", "object_id__id"]



admin.site.register(AccountMetrics, AccountMetricsAdmin)


class AccountInboxAdmin(CustomModelAdmin):
    list_display = ["id", "account", "author", "date", "message"]


admin.site.register(AccountInbox, AccountInboxAdmin)
