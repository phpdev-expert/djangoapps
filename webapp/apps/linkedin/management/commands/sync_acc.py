from webapp.apps.linkedin.tasks import get_page_analytics, get_post_analytics, get_page_follower, \
    linkedin_saved_task, delete_linkedin_page
from django.core.management import BaseCommand
from webapp.apps.linkedin.scripts.sync_all_tasks import sync_all

ACCESS_TOKEN = "AQUqOCAe0UacRtn18u1Dwkxeqeq4tVprONljVNXrsRvulHYBwJ-OTAopcil-EgrnoYFmcvOfW0Eo5BKCD82DJbxcZCPywEO9FdwK96MLEKeTzVbmhYD6mrjMVNeyIoDQr9Q6qaj9WdsAGIzMe2jVZvkvdM_HTDSxkblYC9YAw36loZBAzfTa7Xq0KHUBmJKAYscnQBhuyiqQ1d-CkcgaxlkWHk-rc6qWd-Z-hl1nniYeOfwZ2CR3BzZzIKjmbEewXfxyK7r5KQz4Ds6EvRu1VfTUE0zu8T6WnL_OniGFObnbYCzPq9r-07ytKk4PanRhsIK8FNuGpmix-L2sVlXWEGJ9n6B-Pg"


class Command(BaseCommand):
    def handle(self, *args, **options):
        # sync_all(access_token=ACCESS_TOKEN, auth_id=1)
        data = {'name': 'Norah Ai', 'page_id': '13406193', 'auth_user_id': 10, 'phone': None, 'website': 'https://norah.ai/', 'about': '', 'description': 'A team of professional gamers at heart and data scientists in our minds is what defines us. \r\nOur dream of becoming the largest provider of cutting edge technology to gaming studios across \r\nthe globe is what keeps us up at night. Reach out to us if your passion is gaming as \r\nwe are here to help you in the journey from inception till beyond .', 'cover_url': None, 'picture_url': None, 'access_token': ACCESS_TOKEN, 'status': 'active'}
        app = linkedin_saved_task.apply_async(kwargs={"data":data})
        # delete_linkedin_page.delay(data)
