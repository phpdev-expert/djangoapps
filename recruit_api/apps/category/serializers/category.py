from rest_framework import serializers
from recruit_api.apps.category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('created', 'modified')
