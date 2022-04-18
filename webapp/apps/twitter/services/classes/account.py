from webapp.apps.twitter.models import TwitterAccount, DirectMessages, Mention
from webapp.apps.twitter.serializers.response_serializers.account_serializer import TwitterAccountSerializer, \
    TwitterAccountListSerializer
from webapp.apps.twitter.serializers.response_serializers.inbound_message_serializer import InboundMessageSerializer, \
    InboundTableSerialzer
from webapp.apps.twitter.serializers.response_serializers.mention_serializer import MentionSerializer
from webapp.apps.twitter.serializers.response_serializers.tweet_serializer import TweetSerializer, \
    TweetWithReplySerializer, TweetsTableSerializer
from itertools import chain


class Account:
    user = None
    account = None

    def __init__(self, user, twitter):
        self.user = user
        self.account = twitter

    def get_accounts(self,):
        """
        get specific account details
        :return:
        """
        accounts = self.account
        serializer = TwitterAccountSerializer(instance=accounts)
        return serializer.data

    def get_accounts_list(self):
        serializer = TwitterAccountListSerializer(self.account, many=True)
        return serializer.data

    def get_account_analytic_list(self):
        serializer = TwitterAccountSerializer(self.account, many=True)
        return serializer.data

    def get_accounts_tweets_table(self):
        query = list()
        for acc in self.account:
            query.append(acc.tweets_set.all())
            query.append(acc.tweetreply_set.all())
        tweet_table = chain.from_iterable(query)
        serializer = TweetsTableSerializer(tweet_table, many=True)
        sort = sorted(serializer.data, key=lambda x: x["date"], reverse=True)
        return sort

    def get_accounts_inbound_message_table(self):

        query = list()
        for acc in self.account:
            query.append(DirectMessages.objects.filter(receiver_id=acc.twitter_id))
            query.append(Mention.objects.select_related('tweet', 'reply').prefetch_related("tweet__tweetreply_set",
                                                                                                "reply__tweetreply_set").filter(
                                  twitter_id=acc.twitter_id))
        inbound_table = chain.from_iterable(query)
        serializer = InboundTableSerialzer(inbound_table, many=True)
        sort = sorted(serializer.data, key=lambda x: x["date"], reverse=True)
        return sort

    def get_inbound_message_table(self):
        """
        get specific account inbound messages
        """
        inbound_table = chain(DirectMessages.objects.filter(receiver_id=self.account.twitter_id),
                              Mention.objects.select_related('tweet', 'reply').prefetch_related("tweet__tweetreply_set",
                                                                                                "reply__tweetreply_set").filter(
                                  twitter_id=self.account.twitter_id))

        serializer = InboundMessageSerializer(inbound_table, many=True, context={"account": self.account})
        sort = sorted(serializer.data, key=lambda x: x["date"], reverse=True)
        return sort

    def get_tweet_by_account(self):
        """
        get single account list of tweets
        :return:
        """
        tweets = self.account.tweets_set.all()
        serializer = TweetSerializer(tweets, many=True)
        return serializer.data

    def get_single_tweet(self, tweet_id):
        """
        get single tweet details
        :param tweet_id:
        :return:
        """
        try:
            tweet = self.account.tweets_set.prefetch_related("tweetreply_set").get(tweet_id=tweet_id)
        except:
            raise Exception("Tweet not found")
        serializer = TweetSerializer(tweet)
        return serializer.data

    def get_single_tweet_with_reply(self, tweet_id):
        """
        get single tweet with replies
        """
        try:
            tweet = self.account.tweets_set.prefetch_related("tweetreply_set").get(tweet_id=tweet_id)
        except:
            raise Exception("Tweet not found")
        serializer = TweetWithReplySerializer(tweet)
        return serializer.data



