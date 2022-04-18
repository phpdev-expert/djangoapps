from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from webapp.apps.streams.models import Stream
from webapp.apps.streams.serializers import (StreamDataSerializer,
                                             StreamSerializer)
from webapp.apps.streams.services.stream_resolver_service import \
    StreamResolverService
from webapp.base.base_api import BaseAPIView


class StreamsViewSet(BaseAPIView, ModelViewSet):
    """
    Lists and retrieves streams data
    """

    serializer_class = StreamSerializer
    http_method_names = ["get", "post", "delete", "put"]

    def get_queryset(self):
        """Sets a initial queryset to fetch objects belonging to the user which are active"""
        user_id = self.request.auth_user_id
        return Stream.objects.prefetch_related().filter(
            user_id=user_id, archived_at=None
        )

    def perform_create(self, serializer):
        """Adds user id to the data before save"""
        serializer.save(user_id=self.request.auth_user_id)

    def perform_update(self, serializer):
        """Sets user_id to auth user and allows to update only name"""
        # TODO: test to check only name updates
        if "name" in serializer.validated_data:
            serializer._validated_data = {"name": serializer.validated_data["name"]}
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Deletes an instance and returns a 200 response"""
        instance = self.get_object()
        instance.archived_at = timezone.now()
        instance.save()
        return Response(dict(id=instance.id), status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Fetch the stream along with the data from the network site"""
        # TODO: test pagination and stream data
        instance = self.get_object()
        stream_data = StreamResolverService(instance).fetch_data(
            **self.request.query_params.dict()
        )
        serializer = StreamDataSerializer(instance, context=stream_data)
        return Response(serializer.data)