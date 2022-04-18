from django.conf import settings

import tweepy
from webapp.apps.streams import models
from webapp.apps.streams.utils import paginate_class, paginated_response


@paginate_class(paginated_response)
class TwitterService:
    """
    Given a  Twitter account with a valid access token, fetches the latest data from the account

    Example:
        >>> account = models.Account.objects.exclude(token_secret__isnull=True).filter(type__iexact="twitter").latest('date_created')
        >>> tss = TwitterService(account)
        >>> tss.likes()
    """

    def __init__(self, token: str, token_secret: str):
        """Initializes the class with the twitter credentials and token"""
        auth = tweepy.OAuthHandler(settings.TWITTER_APP_ID, settings.TWITTER_APP_SECRET)
        auth.set_access_token(token, token_secret)
        self.api = tweepy.API(auth)

    def home(self, **kwargs):
        """Fetches all the tweets from home timeline"""
        return self.api.home_timeline(**kwargs)

    def mentions(self, **kwargs):
        """Fetches all the tweets where user is mentioned"""
        return self.api.mentions_timeline(**kwargs)

    def my_tweets(self, **kwargs):
        """Fetches all the tweets by the user"""
        return self.api.user_timeline(**kwargs)

    def likes(self, **kwargs):
        """Fetches all the tweets liked by the user"""
        return self.api.favorites(**kwargs)

    def retweets(self, **kwargs):
        """Fetches all the retweets of the tweets by the user"""
        return self.api.retweets_of_me(**kwargs)

    def new_followers(self, **kwargs):
        """Fetches the list of new followers"""
        return self.api.followers(**kwargs)

    def keyword(self, query: str = '', **kwargs):
        """Searches and fetches all the tweets by a keyword"""
        return self.api.search(query, **kwargs)

    def lists(self, **kwargs):
        """Fetches the lists present in the account"""
        return self.api.lists_all(**kwargs)

    # TODO: fetch scheduled tweets
    # require access to ads api for this
    # https://developer.twitter.com/en/docs/twitter-ads-api/creatives/api-reference/scheduled-tweets