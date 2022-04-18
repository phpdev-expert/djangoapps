from django.core.management import BaseCommand
import tweepy
from webapp.apps.twitter.tasks import sync_account, sync_direct_message, sync_tweets, sync_tweet_reply, \
    twitter_saved_task
from webapp.apps.twitter.scripts.sync_all_tasks import sync_all
from tweepy.error import TweepError


class Command(BaseCommand):
    def handle(self, *args, **options):
        consumer_key = 'fA5VlTK0K6GjIcv9eRHEan2zV'
        consumer_secret = '4a8fm9r7OyRPQEqw3VdbI9mfR4BYfxFaAWwp9obLTP4uf0kNFr'
        access_token = '1073889170320351233-K8JHJYbnkxtbYkzw4HFC1WzxQ1j2s'
        access_token_secret = 'DBoaDTeW5yPvTYbGBp1wN8ZrXvHdRmxQuXbzVfbO5wu44'
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        user_id = '1073889170320351233'
        data = {'social_account_id': '1073889170320351233', 'access_token': '1073889170320351233-1wKytRxChZL1ewu6TnS9a2yJNrHeQY', 'access_token_secret': 'suRRNWm9jH128iYQkmrdYjEYviVdbavPqOpju7vNtSXtJ', 'first_name': 'PyxisPm', 'last_name': '', 'screen_name': 'PmPyxis', 'email': '', 'auth_user_id': 3, 'account_type': '', 'status': 'active'}
        # sync_all(twitter_id=user_id, access_token=access_token,access_token_secret=access_token_secret, auth_id=1)
        twitter_saved_task.delay(data=data)
