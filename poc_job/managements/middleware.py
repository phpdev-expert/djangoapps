from django.http import HttpResponseRedirect
from django.urls import reverse
from managements.models import AdminUsers
from django.core.urlresolvers import resolve
from django.shortcuts import redirect
from django.conf import settings
from datetime import date
import datetime

class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        current_url = resolve(request.path_info).url_name
        if request.user.is_authenticated():
            user=AdminUsers.objects.get(pk=request.user.pk)
            datetimeObj1 = user.is_login
            latpdate=user.last_password_change
            if latpdate:
                d0 = latpdate.date()
            else:
                d0 = datetime.date.today()

            d1 = datetime.date.today()
            delta = d1 - d0
            exp=settings.PASSWORD_EXPIRY_DURATION
            if datetimeObj1==0 or datetimeObj1 == None:
                if current_url!='change_password':
                    return redirect('/password')

            if delta.days>=exp:
                if current_url!='change_password':
                    return redirect('/password')
        return response
