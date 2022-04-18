from rest_framework import serializers

from webapp.apps.linkedin.models import LinkedinAccount, Page
from drf_writable_nested import WritableNestedModelSerializer


def get_page_by_id(id):
    try:
        return Page.objects.get(page_id=id)
    except :
        return None


def get_page_by_id_and_user_id(id, user_id):
    try:
        return Page.objects.get(page_id=id, user_id=user_id)
    except :
        return None


class LinkedInAccountSerializer(WritableNestedModelSerializer):
    class Meta:
        model = LinkedinAccount
        fields = [
            "user_id",
            "linkedin_id",
            "access_token"
        ]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "user_id",
            "page_id",
            "name",
            "access_token",
            "phone",
            "website",
            "about",
            "description",
            "cover_url",
            "picture_url",
            "status",
            "message",
            "last_sync_time",
            "sync_status"
        ]
