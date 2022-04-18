from rest_framework import serializers

from webapp.apps.twitter.models import Tweets, Mention, DirectMessages, TweetReply
from webapp.apps.twitter.serializers.response_serializers.direct_message_serializer import InboundDirectMessageSerializer
from webapp.apps.twitter.serializers.response_serializers.mention_serializer import MentionSerializer


class InboundMessageSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        # data = super().to_representation(instance)
        data = dict()
        if isinstance(instance, Mention):
            serializer = MentionSerializer(instance)
            data = serializer.data
        if isinstance(instance, DirectMessages):
            serializer = InboundDirectMessageSerializer(instance)
            data = serializer.data
        data["user"] = self.context.get("account").screen_name
        return data


class InboundTableSerialzer(serializers.Serializer):
    def to_representation(self, instance):
        # data = super().to_representation(instance)
        data = dict()
        if isinstance(instance, Mention):
            serializer = MentionSerializer(instance)
            data = serializer.data
        if isinstance(instance, DirectMessages):
            serializer = InboundDirectMessageSerializer(instance)
            data = serializer.data
        # data["user"] = self.context.get("account").screen_name
        return data