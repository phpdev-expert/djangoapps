from celery import shared_task
from django.conf import settings
from datetime import datetime
from webapp.apps.metrics.data_loader.facebook import FacebookDataLoader
from webapp.apps.api.cache import Cacher
from datetime import date

import logging

log = logging.getLogger("facebook")

@shared_task(bind=True, name=settings.FACEBOOK_SYNC_MESSAGES_TASK)
def facebook_sync_comments(self, data=None):
    log.info("facebook_sync_comments")
    print(data)
    if data:
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("page_id")
        dataLoader = FacebookDataLoader(user_id=auth_user_id, page_id=page_id)
        try:
            dataLoader.sync_comments()
        except Exception as msg:
            log.info(f"commments : {msg}")
        try:
            dataLoader.sync_message()
        except Exception as msg:
            log.info(f"messsage : {msg}")
        page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        now = datetime.now()
        page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        if page.sync_status == "pending" or page.sync_status == "progress":
            page.error = ""
            page.sync_status = "ok"
        page.save()
        Cacher.delete(f"stat_health_{auth_user_id}")
        Cacher.delete_pattern(('metrics_{}_*').format(auth_user_id))

@shared_task(bind=True, name=settings.FACEBOOK_PAGE_SYNC_ACTION_TASK)
def facebook_sync_action_task(self, data=None, params={"initial_sync": False}):
    log.info("fb_sync_account")
    log.info(data)
    log.info(params)
    if data:
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("page_id")
        dataLoader = FacebookDataLoader(user_id=auth_user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        last_synced = page.last_synced
        page.sync_status = "progress"
        now = datetime.now()
        page.last_synced = now.strftime("%Y-%m-%d %H:%M:%S")
        page.save()
        params["initial_sync"] = True
        if not params["initial_sync"]:
            params["since"] = settings.SYNC_SINCE
            if last_synced:
                params["since"] = last_synced.strftime("%Y-%m-%d")
            params["until"] = date.today().strftime("%Y-%m-%d")
        try:
            dataLoader.fetch_insights(params)
        except Exception as msg:
            log.info(f"fetch_insights : {msg}")
        try:
            dataLoader.sync_post_and_video("post", params)
        except Exception as msg:
            log.info(f"sync_post : {msg}")
        try:
            dataLoader.sync_post_and_video("video", params)
        except Exception as msg:
            log.info(f"sync_video : {msg}")

        facebook_sync_comments.delay(data)

        # page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        # now = datetime.now()
        # page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        # if page.sync_status == "pending" or page.sync_status == "progress":
        #     page.error = ""
        #     page.sync_status = "ok"
        # page.save()
        Cacher.delete(f"stat_health_{auth_user_id}")
        Cacher.delete_pattern(('metrics_{}_*').format(auth_user_id))


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_SYNC_TASK)
def facebook_sync_task(self, data=None, params={"initial_sync": False}):
    log.info("fb_page_sync")
    log.info(data)
    if data:
        status = data.get("status")
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("page_id")
        if status == "deleted":
            # just update the account status as deleted and not remove the data
            dataLoader = FacebookDataLoader(user_id=auth_user_id, page_id=page_id)
            try:
                created = dataLoader.save_page(data=dict(data))
                Cacher.delete(f"stat_health_{auth_user_id}")
            except Exception as msg:
                log.info(f"page_save_exception : {msg}")
        if status == "active":
            dataLoader = FacebookDataLoader(user_id=auth_user_id, page_id=page_id)
            created = False
            try:
                created = dataLoader.save_page(data=dict(data))
            except Exception as msg:
                log.info(f"page_save_exception : {msg}")
            try:
                if created:
                    params["initial_sync"] = True
                log.info("Start page sync")
                facebook_sync_action_task.delay(data, params)
            except Exception as msg:
                log.info(f"Page sync failed : {msg}")
            # try:
            #     if created:
            #         params["initial_sync"] = True
            #     dataLoader.fetch_insights(params)
            # except Exception as msg:
            #     log.info(f"fetch_insights : {msg}")
            # try:
            #     dataLoader.sync_post_and_video("post", params)
            # except Exception as msg:
            #     log.info(f"sync_post : {msg}")
            #
            # try:
            #     dataLoader.sync_post_and_video("video", params)
            # except Exception as msg:
            #     log.info(f"sync_video : {msg}")
            #
            # try:
            #     dataLoader.sync_comments(params)
            # except Exception as msg:
            #     log.info(f"commments : {msg}")
            #
            # try:
            #     dataLoader.sync_message(params)
            # except Exception as msg:
            #     log.info(f"messsage : {msg}")
            #
            # page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
            # now = datetime.now()
            # page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
            # page.save()


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_DELETE_ACTION_TASK)
def delete_facebook_page_action(self, data=None):
    log.info("delete_facebook_page_action")
    log.info(data)
    if data:
        user_id = data.get("auth_user_id")
        page_id = data.get("page_id")
        dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.accountobject_set.all().delete()
                page.accountinbox_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_DELETE_TASK)
def delete_facebook_page(self, data=None):
    log.info("fb_page_delete_task")
    log.info(data)
    delete_facebook_page_action.delay(data)
    # if data:
    #     user_id = data.get("auth_user_id")
    #     page_id = data.get("page_id")
    #     dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    #     page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    #     if page:
    #         try:
    #             page.accountmetrics_set.all().delete()
    #             page.accountobject_set.all().delete()
    #             page.accountinbox_set.all().delete()
    #             page.delete()
    #             Cacher.delete(f"stat_health_{user_id}")
    #         except Exception as msg:
    #             log.info(msg)


@shared_task(bind=True, name=settings.FACEBOOK_GROUP_DELETE_TASK)
def delete_facebook_group(self, data=None):
    log.info("fb_group_delete")
    log.info(data)
    delete_facebook_page_action.delay(data)
    # if data:
    #     user_id = data.get("auth_user_id")
    #     page_id = data.get("page_id")
    #     dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    #     page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    #     if page:
    #         try:
    #             page.accountmetrics_set.all().delete()
    #             page.accountobject_set.all().delete()
    #             page.accountinbox_set.all().delete()
    #             page.delete()
    #             Cacher.delete(f"stat_health_{user_id}")
    #         except Exception as msg:
    #             log.info(msg)


## Todo ##
@shared_task(bind=True, name=settings.FACEBOOK_PAGE_COMMENTS_SYNC_TASK)
def fetch_post_comments(self, user_id, page_id, params={"initial_sync": False}):
    log.info("fb_sync_post_comments", page_id)
    dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    if page:
        try:
            dataLoader.sync_message(params)
        except Exception as msg:
            print("sync_comments_failed ", msg)


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_MESSAGE_SYNC_TASK)
def fetch_page_message(self, user_id, page_id, params={"initial_sync": False}):
    log.info("fb_page_message")
    log.info(page_id)
    dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    if page:
        try:
            dataLoader.sync_message(params)
        except Exception as msg:
            log.info(f"messsage : {msg}")


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_POST_SYNC_TASK)
def fetch_page_post_metrics_task(
    self, user_id, page_id, params={"initial_sync": False}
):
    log.info("fb_sync_page_metrics", page_id)
    dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    if page:
        try:
            dataLoader.sync_post_and_video("post", params)
        except Exception as msg:
            print("sync_post ", msg)
        try:
            dataLoader.sync_post_and_video("video", params)
        except Exception as msg:
            print("sync_video ", msg)


@shared_task(bind=True, name=settings.FACEBOOK_PAGE_VIDEO_SYNC_TASK)
def fetch_page_video_metrics_task(self, user_id, page_id, pagination=None):
    dataLoader = FacebookDataLoader(user_id=user_id, page_id=page_id)
    page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    if page:
        try:
            dataLoader.sync_post_and_video("video")
        except Exception as msg:
            print("exception ", msg)
