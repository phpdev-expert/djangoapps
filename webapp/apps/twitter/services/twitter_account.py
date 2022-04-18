from rest_framework.exceptions import ValidationError
from webapp.apps.twitter.models import TwitterAccount
from webapp.apps.twitter.serializers.twitter_account_serializer import TwitterAccountSerializer, \
    SyncAccountInfoSerializer
from datetime import datetime

def get_twitter_acc_by_id(id):
    """
    Get Twitter Account By Id
    :param id:
    :return:
    """
    try:
        return TwitterAccount.objects.get(twitter_id=id)
    except TwitterAccount.DoesNotExist:
        return None

def get_twitter_acc_by_id_and_user_id(id, user_id=None):
    """
    Get Twitter Account By Id
    :param id:
    :return:
    """
    try:
        return TwitterAccount.objects.get(twitter_id=id, auth_user_id=user_id)
    except TwitterAccount.DoesNotExist:
        return None


def save_authenticated_user(user, auth_id):
    """
    save Authenticated User Info
    :param user:
    :param access_token:
    :param auth_id:
    :return:
    """
    try:
        json = user._json
        json.pop("status")
        get_acc = get_twitter_acc_by_id_and_user_id(json['id_str'], auth_id)
        now = datetime.now()
        json['last_sync_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
        json['sync_status'] = TwitterAccount.OK
        json['message'] = "Sync Success"
        serializer = TwitterAccountSerializer(data=json, instance=get_acc, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    except Exception as msg:
        print("exception s: %s" % msg)


def save_twitter_account_status(twitter_id, auth_user_id, status=None, sync_status=None, sync_time=None, message=None):
    data = dict()

    if status:
        data["status"] = status
    if sync_status:
        data["sync_status"] = sync_status
    if sync_time:
        data['last_sync_time'] = sync_time
    data["message"] = message

    instance = get_twitter_acc_by_id_and_user_id(twitter_id, auth_user_id)
    serializer = SyncAccountInfoSerializer(instance=instance, data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return instance
