from rest_framework import serializers

from webapp.apps.twitter.models import DirectMessages
from webapp.apps.twitter.services.twitter_account import get_twitter_acc_by_id


class InboundDirectMessageSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="Direct Message")
    date = serializers.CharField(source="message_date")
    message = serializers.CharField(source="text")

    class Meta:
        model = DirectMessages
        fields = [
            "type",
            "message",
            "date"
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        sender = get_twitter_acc_by_id(instance.sender_id)
        receiver = get_twitter_acc_by_id(instance.receiver_id)
        if sender:
            data["language"] = sender.language
            data["country"] = sender.location
            data["author"] = sender.screen_name
        else:
            data["language"] = ""
            data["country"] = ""
            data["author"] = ""
        data["screen_name"] = receiver.screen_name if receiver else ""
        return data