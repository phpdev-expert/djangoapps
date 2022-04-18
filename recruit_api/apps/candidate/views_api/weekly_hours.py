from rest_framework import viewsets
from rest_framework import generics
from recruit_api.apps.candidate.models.candidate import WeekyHours
from recruit_api.apps.candidate.serializers.weeky_hours import WeekyHoursSerializer

class WeekHourView(viewsets.ModelViewSet):
    serializer_class = WeekyHoursSerializer
    queryset = WeekyHours.objects.all()
    def get_queryset(self):
        candidate = self.request.query_params.get('candidate')
        fromd = self.request.query_params.get('month')
        if candidate:
            if fromd :
                queryset = WeekyHours.objects.filter(candidate=candidate).filter(start_date__month=fromd)
            else:
                queryset = WeekyHours.objects.filter(candidate=candidate)
        else:
            queryset = WeekyHours.objects.all()
        return queryset
