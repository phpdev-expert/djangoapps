from rest_framework import serializers

from webapp.apps.metrics.models import AccountObject
import json

class RecentPostSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source="account.type")
    id = serializers.CharField(source="object_id")
    time = serializers.CharField(source="date_posted")

    class Meta:
        model = AccountObject
        fields = ("id", "platform", "title", "time", "description", "date_posted")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        data = dict()
        if representation["platform"] == "twitter":
            data = self.filter_twitter(instance)
        if representation["platform"] == "linkedin":
            data = self.filter_linkedin(instance)
        if representation["platform"] == "facebook":
            data = self.filter_facebook(instance)
        if representation["platform"] == "instagram":
            data = self.filter_instagram(instance)
        data.update({
            "page": {
                "id": instance.account.page_id,
                "name": instance.account.name,
                "picture_url": instance.account.data.get("profile_pic_url") if instance.account.data else None
            }
        })

        representation.update(data)
        return representation

    def filter_twitter(self, instance):
        metric = {"likes": 0, "comments": 0, "engagement": 0}
        post_metrics = instance.accountmetrics_set.all()
        reply = instance.twitterreply_set.count()
        for m in post_metrics:
            if m.metrics.metric == "favourites_count":
                metric["likes"] = m.value
                try:
                    metric["engagement"] += int(m.value)
                except:
                    pass
            if m.metrics.metric == "replies_count" or m.metrics.metric == "retweet_count":
                try:
                    metric["engagement"] += int(m.value)
                except:
                    pass

        metric["comments"] = reply
        metric["url"] = instance.data["media"]
        return metric

    def filter_linkedin(self, instance):
        data = {"likes": 0, "comments": 0, "engagement":0}
        post_metrics = instance.accountmetrics_set.all()
        for metric in post_metrics:
            if metric.metrics.metric == "likeCount":
                data["likes"] = metric.value
            if metric.metrics.metric == "commentCount":
                data["comments"] = metric.value
            if metric.metrics.metric == "engagement":
                data["engagement"] = metric.value
        data["url"] = instance.data["media"]
        return data

    def filter_facebook(self, instance):
        data = {"likes": 0, "comments": 0}
        post_metrics = instance.accountmetrics_set.all()
        for metric in post_metrics:
            if metric.metrics.metric == "post_reactions_like_total":
                data["likes"] = metric.value
            if metric.metrics.metric == "post_reactions_by_type_total":
                total_reaction = 0
                for i in json.loads(metric.value.replace('\'','\"')).values():
                    total_reaction = total_reaction + int(i)
                data["engagement"] = total_reaction
        data["comments"] = instance.data.get("comment_count", 0) if instance.data else 0
        data["url"] = [instance.data.get("media_url","")] if instance.data else []

        return data

    def filter_instagram(self, instance):
        data = {"likes": 0, "comments": 0, "engagement": 0}
        post_metrics = instance.accountmetrics_set.all()
        for metric in post_metrics:
            if metric.metrics.metric == "impressions":
                data["engagement"] += metric.value
        if instance.data:
            data["likes"] = instance.data.get("like_count", 0)
            data["comments"] = instance.data.get("comments_count", 0)
            data["engagement"] += instance.data.get("like_count", 0) + instance.data.get("comments_count", 0) + instance.data.get("impressions",0)
        data["url"] = [instance.data["media_url"]]

        return data
