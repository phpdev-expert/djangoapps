from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import viewsets
from recruit_api.apps.category.models import *
from recruit_api.apps.category.serializers import CategorySerializer

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
