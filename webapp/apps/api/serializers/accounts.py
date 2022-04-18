# -*- coding: utf-8 -*-
from rest_framework import serializers

from webapp.apps.metrics.models import Account, AccountInbox, TwitterMention


class AccountObjectSerializer(serializers.Serializer):
    id = serializers.CharField(source="object_id")
    page_id = serializers.CharField(source="account.page_id")
    title = serializers.CharField()
    description = serializers.CharField()
    date_posted = serializers.DateTimeField()
    data = serializers.SerializerMethodField()

    class Meta:
        fields = ("id", "title", "description", "date_posted", "data")

    def get_data(self, instance):
        res = instance.data
        acc_type = instance.account.type
        if acc_type == "twitter":
            data = {"retweet_count": 0, "likes": 0, "replies": 0}
            post_metrics = instance.accountmetrics_set.all()
            reply = instance.twitterreply_set.count()
            for m in post_metrics:
                if m.metrics.metric == "favourites_count":
                    data["likes"] = m.value
                if m.metrics.metric == "retweet_count":
                    data["retweet_count"] = m.value
            data["replies"] = reply
            data[
                "permalink"
            ] = f"https://twitter.com/{instance.account.name}/status/{instance.object_id}"
            res.update(data)
        elif acc_type == "facebook":
            instance.data["permalink"] = "https://facebook.com/{}".format(
                instance.object_id
            )
        elif acc_type == "linkedin":
            instance.data["permalink"] = "https://linkedin.com/feed/update/{}".format(
                instance.object_id
            )
        return res


class AccountSignalResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class InboundTableSerialzer(serializers.Serializer):
    def to_representation(self, instance):
        data = dict()
        data["page_id"] = instance.account.page_id
        if isinstance(instance, TwitterMention):
            # try:
            #     tweet = AccountObject.objects.filter(object_id=instance.mention_id).first()
            #     data["message"] = tweet.title
            #     data["author"] = tweet.data.get("author")
            # except:
            #     tweet = None
            # try:
            #     reply = TwitterReply.objects.filter(reply_id=instance.mention_id).first()
            #     data["message"] = reply.description
            #     data["author"] = reply.data.get("author")
            # except:
            #     reply = None
            # # data["author"] = ""
            # if reply or tweet:
            #     pass
            # else:
            #     print(instance.mention_id)
            data["author"] = instance.data.get("author") if instance.data else None
            data["message"] = instance.data.get("title") if instance.data else None
            data["type"] = "Mention"
            data["date"] = instance.date
        if isinstance(instance, AccountInbox):
            data["type"] = "Message"
            data["message"] = instance.message
            data["author"] = instance.author
            data["date"] = instance.date
        # data["user"] = self.context.get("account").screen_name
        return data


class SyncCompletedTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("page_id", "name", "sync_completed")


class SyncApiSerializer(serializers.Serializer):
    type = serializers.CharField(required=False)
    page_id = serializers.CharField(required=False)
    manual = serializers.BooleanField(required=False, default=False)
