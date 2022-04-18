import json

from django.db import connection

from rest_framework import serializers
from webapp.apps.streams.constants import STREAM_TYPE
from webapp.apps.streams.models import Stream


class StreamSerializer(serializers.ModelSerializer):
    """
    Serializes the Streams data. Used for CRUD operations

     Sample Payload:
     id: 1
     name: 'My Tweets'
     type: 'HOME'
     terms: ['#django']
     board_id: 14
     """

    class Meta:
        model = Stream
        fields = (
            "id",
            "name",
            "type",
            "terms",
            "board",
            "user_id",
            "account",
        )
        extra_kwargs = {
            'user_id': {'read_only': True}
        }

    def validate_type(self, value):
        """
        Check stream type is a valid.
        """
        # TODO: stream type test
        if value not in STREAM_TYPE:
            raise serializers.ValidationError("Invalid stream type")
        return value

    def validate_board(self, board):
        """
        Validation board belongs to user
        """
        # TODO: board test
        user_id = self.context['request'].auth_user_id
        if board.user_id != user_id:
            raise serializers.ValidationError("Board does not exist")
        return board

    def validate_account(self, account):
        """
        Validate account id belongs to user
        """
        # TODO: account test
        user_id = self.context['request'].auth_user_id
        if int(account.user_id) != user_id:
            raise serializers.ValidationError("Account does not exist")
        return account

    def validate_terms(self, value):
        # TODO: terms saves properly
        """
        Parses terms to a string of arrays
        "hello, world" -> ["hello", "world"]
        """
        value = tuple(map(lambda x: x.strip(), value[0].split(",")))
        return value


class StreamDataSerializer(serializers.ModelSerializer):
    """
    Serializes the Stream data along with the content received from social network. Used
    when retrieving the stream.
     """

    data = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    first_id = serializers.SerializerMethodField()
    next_id = serializers.SerializerMethodField()

    class Meta:
        model = Stream
        fields = (
            "id",
            "name",
            "type",
            "terms",
            "board",
            "user_id",
            "account",
            "data",
            "page",
            "size",
            "first_id",
            "next_id"
        )

    def get_data(self, _obj):
        return self.context.get("content", [])

    def get_page(self, _obj):
        return self.context.get("page", None)

    def get_size(self, _obj):
        return self.context.get("size", None)

    def get_first_id(self, _obj):
        return self.context.get("first_id", None)

    def get_next_id(self, _obj):
        return self.context.get("next_id", None)