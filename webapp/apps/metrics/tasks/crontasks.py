from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from webapp.apps.metrics.data_loader.facebook import FacebookDataLoader
from webapp.apps.metrics.data_loader.instagram import InstagramDataLoader
from webapp.apps.metrics.data_loader.linkedin import LinkedinDataLoader
from webapp.apps.metrics.data_loader.twitter import TwitterDataLoader
from webapp.apps.metrics.models import Account
from webapp.apps.metrics.tasks.linkedin import linkedin_saved_task, linkedin_sync_post, linkedin_sync_action_task
from webapp.apps.metrics.tasks.twitter import twitter_sync_action_task
from datetime import date, datetime


@periodic_task(run_every=(crontab(minute=0, hour="*/6")), name="fetch-metrics", queue="daily_sync_queue")
def fetch_metrics_task():
    for page in Account.objects.filter(status="active").all():
        if page.status == "active":
            print(f"{page.page_id} dailysync")
            params={"initial_sync": False}
            params["since"] = settings.SYNC_SINCE
            if page.last_synced:
                params["since"] = page.last_synced.strftime("%Y-%m-%d")
            params["until"] = date.today().strftime("%Y-%m-%d")
            now = datetime.now()
            page.last_synced = now.strftime("%Y-%m-%d %H:%M:%S")
            page.save()
            if page.type == "facebook":
                # facebook_data = {
                #     "auth_user_id": page.user_id,
                #     "page_id": page.page_id,
                #     "status": page.status,
                # }
                # facebook_sync_action_task.delay(
                #     data=facebook_data, params=params
                # )
                dataLoader = FacebookDataLoader(user_id=page.user_id, page_id=page.page_id)
                try:
                    dataLoader.fetch_insights(params=params)
                except Exception:
                    pass
                try:
                    dataLoader.sync_post_and_video("post",params=params)
                except Exception as msg:
                    print("post exception ", msg)

                try:
                    dataLoader.sync_post_and_video("video",params=params)
                except Exception as msg:
                    print("video exception ", msg)

                try:
                    dataLoader.sync_comments(params)
                except Exception as msg:
                    print.info(f"commments : {msg}")
                try:
                    dataLoader.sync_message(params)
                except Exception as msg:
                    print.info(f"messsage : {msg}")

            elif page.type == "instagram":
                instagram_data = {
                    "auth_user_id": page.user_id,
                    "social_account_id": page.page_id,
                    "status": page.status,
                }
                # instagram_sync_action_task.delay(data=instagram_data)
                dataLoader = InstagramDataLoader(user_id=page.user_id, page_id=page.page_id)
                try:
                    dataLoader.fetch_insights(params=params)
                except Exception as exc:
                    print(exc)
                try:
                    dataLoader.sync_post(params=params)
                except Exception as exc:
                    print("post exception", exc)
                try:
                    dataLoader.sync_comments()
                except Exception as exc:
                    print("comments exception", exc)

            elif page.type == "twitter":
                # twitter_data = {
                #     "social_account_id": page.page_id,
                #     "access_token": page.token,
                #     "access_token_secret": page.token_secret,
                #     "screen_name": page.name,
                #     "auth_user_id": page.user_id,
                #     "status": page.status,
                # }
                # twitter_sync_action_task.delay(data=twitter_data)
                dataLoader = TwitterDataLoader(user_id=page.user_id, page_id=page.page_id)
                try:
                    dataLoader.fetch_metrics()
                except Exception as exc:
                    print(exc)

            elif page.type == "linkedin":
                # linkedin_data = {
                #     "auth_user_id": page.user_id,
                #     "page_id": page.page_id,
                #     "name": page.name,
                #     "access_token": page.token,
                #     "status": page.status,
                #     "description": page.description,
                # }
                # linkedin_sync_action_task.delay(data=linkedin_data)
                dataLoader = LinkedinDataLoader(user_id=page.user_id, page_id=page.page_id)
                try:
                    dataLoader.fetch_insights()
                except Exception as exc:
                    print(exc)
                try:
                    linkedin_sync_post(user_id=page.user_id, page_id=page.page_id)
                except Exception as exc:
                    print(exc)

@shared_task(queue="default_queue")
def test():
    print("tttt")
    for i in range(11):
        print("test")