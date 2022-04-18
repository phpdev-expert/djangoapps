from webapp.apps.twitter.models import DirectMessages
from drf_writable_nested import WritableNestedModelSerializer


class DirectMessageSerializer(WritableNestedModelSerializer):
    """
    Direct Messages Serializer
    """
    class Meta:
        model = DirectMessages

        fields = [
            'message_id',
            'sender_id',
            'receiver_id',
            'text',
            'message_date'
        ]
