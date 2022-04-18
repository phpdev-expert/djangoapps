from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from webapp.apps.streams.models import Board
from webapp.apps.streams.permissions import BoardPermission
from webapp.apps.streams.serializers import BoardSerializer
from webapp.base.base_api import BaseAPIView


class BoardsViewSet(BaseAPIView, ModelViewSet):
    """
    Lists and retrieves streams data
    """

    serializer_class = BoardSerializer
    http_method_names = ["get", "post", "delete", "put"]
    permission_classes = [BoardPermission]

    def get_queryset(self):
        """Sets a initial queryset to fetch objects belonging to the user which are active"""
        user_id = self.request.auth_user_id
        return Board.objects.prefetch_related().filter(user_id=user_id, archived_at=None)

    def perform_create(self, serializer):
        """Sets streams_position to empty list on create and user_id to auth user"""
        serializer.save(streams_position=[], user_id=self.request.auth_user_id)

    def perform_update(self, serializer):
        """Sets user_id to auth user"""
        serializer.save(user_id=self.request.auth_user_id)

    def destroy(self, request, *args, **kwargs):
        """Deletes an instance and returns a 200 response"""
        instance = self.get_object()
        instance.archived_at = timezone.now()
        instance.save()
        return Response(dict(id=instance.id), status=status.HTTP_200_OK)