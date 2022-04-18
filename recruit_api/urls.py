"""recruit_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
from recruit_api.apps.candidate.views_api.third_party import ThirdPartyAPIView
from recruit_api.apps.candidate.views_api.third_party import ThirdPartyDetail
from recruit_api.apps.job.views_api.job import VisaStatusAPIView
from recruit_api.apps.job.views_api.job import VisaStatusDetail
from django.conf.urls.static import static
admin.site.site_header ="Anew Recruit Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),

    path(r'api/api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path(f'{settings.BASE_API_URL}user/', include('recruit_api.apps.core.user.urls_api')),
    path(f'{settings.BASE_API_URL}account_manager/', include('recruit_api.apps.account_manager.urls_api')),
    path(f'{settings.BASE_API_URL}third-party/', ThirdPartyAPIView.as_view()),
    path(f'{settings.BASE_API_URL}job/visa-status/', VisaStatusAPIView.as_view()),
    path(f'{settings.BASE_API_URL}third-party/<int:pk>/', ThirdPartyDetail.as_view()),
    path(f'{settings.BASE_API_URL}job/visa-status/<int:pk>/', VisaStatusDetail.as_view()),
    path(f'{settings.BASE_API_URL}candidate/',include('recruit_api.apps.candidate.urls_api')),
    path(f'{settings.BASE_API_URL}client/', include('recruit_api.apps.client.urls_api')),
    path(f'{settings.BASE_API_URL}clients/', include('recruit_api.apps.client.clients_api')),
    path(f'{settings.BASE_API_URL}category/', include('recruit_api.apps.category.urls_api')),
    path(f'{settings.BASE_API_URL}skill/', include('recruit_api.apps.job.skill_url')),
    path(f'{settings.BASE_API_URL}job/', include('recruit_api.apps.job.urls_api')),
    path(f'{settings.BASE_API_URL}email/', include('recruit_api.apps.email.urls_api'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
