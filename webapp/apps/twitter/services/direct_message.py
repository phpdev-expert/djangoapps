from webapp.apps.twitter.models import DirectMessages, TwitterAccount
from webapp.apps.twitter.services.twitter_account import get_twitter_acc_by_id
from webapp.apps.twitter.serializers.direct_message_serializer import DirectMessageSerializer
import time


def get_direct_message_by_id(id):
    """
    get direct message by message_id
    :param id:
    :return:
    """
    try:
        message = DirectMessages.objects.get(message_id=id)
        return message
    except Exception as exc:
        return None


def save_received_messages(messages):
    """
    save received direct messages from twitter account
    :param messages:
    :return:
    """
    try:

        for message in messages:
            data = dict()
            get_message = get_direct_message_by_id(message["id"])
            if get_message is None:
                data['message_id'] = message["id"]
                data['sender_id'] = message["message_create"]['sender_id']
                data['receiver_id'] = message["message_create"]['target']['recipient_id']
                data['text'] = message["message_create"]['message_data']['text']
                data['message_date'] = time.strftime('%Y-%m-%d %H:%M:%S',  time.gmtime(int(message["created_timestamp"])/1000.))
                serializer = DirectMessageSerializer(data=data, instance=get_message, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
    except Exception as exc:
        print("dm services err : {}".format(exc))


