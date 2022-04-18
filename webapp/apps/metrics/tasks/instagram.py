from celery import shared_task
from django.conf import settings
from datetime import datetime
from webapp.apps.metrics.data_loader.instagram import InstagramDataLoader
from webapp.apps.api.cache import Cacher
from datetime import date

import logging

log = logging.getLogger("instagram")

@shared_task(bind=True, name=settings.INSTAGRAM_SYNC_MESSAGES_TASK)
def instagram_sync_comments(self, data=None):
    log.info("instagram_sync_comments")
    print(data)
    if data:
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
        try:
            dataLoader.sync_comments()
        except Exception as exc:
            log.info("comments exception", exc)
        page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        now = datetime.now()
        page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        if page.sync_status == "pending" or page.sync_status == "progress":
            page.error = ""
            page.sync_status = "ok"
        page.save()
        Cacher.delete(f"stat_health_{auth_user_id}")
        Cacher.delete_pattern(('metrics_{}_*').format(auth_user_id))

@shared_task(bind=True, name=settings.INSTAGRAM_SYNC_ACTION_TASK)
def instagram_sync_action_task(self, data=None, params={"initial_sync": False}):
    log.info("instagram_sync_action_task", data)
    if data:
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        last_synced = page.last_synced
        page.sync_status = "progress"
        now = datetime.now()
        page.last_synced = now.strftime("%Y-%m-%d %H:%M:%S")
        page.save()
        if not params["initial_sync"]:
            params["since"] = settings.SYNC_SINCE
            if last_synced:
                params["since"] = last_synced.strftime("%Y-%m-%d")
            params["until"] = date.today().strftime("%Y-%m-%d")
        try:
            dataLoader.fetch_insights(params)
        except Exception as exc:
            log.info(exc)
        try:
            dataLoader.sync_post(params)
        except Exception as exc:
            log.info("post exception", exc)

        instagram_sync_comments.delay(data)
        # try:
        #     dataLoader.sync_comments(params)
        # except Exception as exc:
        #     log.info("comments exception", exc)
        # page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
        # now = datetime.now()
        # page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        # if page.sync_status == "pending" or page.sync_status == "progress":
        #     page.error = ""
        #     page.sync_status = "ok"
        # page.save()
        Cacher.delete(f"stat_health_{auth_user_id}")
        Cacher.delete_pattern(('metrics_{}_*').format(auth_user_id))


@shared_task(bind=True, name=settings.INSTAGRAM_BUSINESS_ACCOUNT_SYNC_TASK)
def instagram_business_sync_task(self, data=None):
    log.info("insta_business_sync", data)
    if data:
        status = data.get("status")
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        if status == "deleted":
            dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
            try:
                dataLoader.save_page(data=data)
                Cacher.delete(f"stat_health_{auth_user_id}")
            except Exception as exc:
                log.info(exc)
        if status == "active":
            dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
            params = {"initial_sync": False}
            try:
                params["initial_sync"] = dataLoader.save_page(data=data)
            except Exception as exc:
                log.info(exc)
            try:
                log.info("start instagram business page sync")
                instagram_sync_action_task.delay(data, params)
            except Exception as msg:
                log.info(f"instagram business page sync failed : {msg}")
        #     try:
        #         dataLoader.fetch_insights(params)
        #     except Exception as exc:
        #         log.info(exc)
        #     try:
        #         dataLoader.sync_post(params)
        #     except Exception as exc:
        #         log.info("post exception", exc)
        #     try:
        #         dataLoader.sync_comments(params)
        #     except Exception as exc:
        #         log.info("comments exception", exc)
        # Cacher.delete(f"stat_health_{auth_user_id}")


@shared_task(bind=True, name=settings.INSTAGRAM_ACCOUNT_SYNC_TASK)
def instagram_sync_task(self, data=None):
    log.info("insta_account_sync", data)
    if data:
        status = data.get("status")
        params = {"initial_sync": False}
        auth_user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        if status == "deleted":
            dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
            try:
                dataLoader.save_page(data=data)
                Cacher.delete(f"stat_health_{auth_user_id}")
            except Exception as exc:
                log.info(exc)
        if status == "active":
            dataLoader = InstagramDataLoader(user_id=auth_user_id, page_id=page_id)
            try:
                params["initial_sync"] = dataLoader.save_page(data=data)
            except Exception as exc:
                log.info(exc)
            try:
                log.info("start instagram page sync")
                instagram_sync_action_task.delay(data, params)
            except Exception as msg:
                log.info(f"instagram page sync failed : {msg}")
            # try:
            #     dataLoader.fetch_insights(params)
            # except Exception as exc:
            #     log.info(exc)
            # try:
            #     dataLoader.sync_post(params)
            # except Exception as exc:
            #     log.info("post exception", exc)
            # try:
            #     dataLoader.sync_comments(params)
            # except Exception as exc:
            #     log.info("comments exception", exc)
            # page = dataLoader.get_page(user_id=auth_user_id, page_id=page_id)
            # now = datetime.now()
            # page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
            # page.save()


@shared_task(bind=True, name=settings.INSTAGRAM_ACCOUNT_DELETE_TASK)
def delete_instagram_account(self, data=None):
    log.info("insta_delete_account", data)
    if data:
        user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        dataLoader = InstagramDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.accountobject_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)


@shared_task(bind=True, name=settings.INSTAGRAM_BUSINESS_ACCOUNT_DELETE_TASK)
def delete_instagram_business_account(self, data=None):
    log.info("insta_delete_business", data)
    if data:
        user_id = data.get("auth_user_id")
        page_id = data.get("social_account_id")
        dataLoader = InstagramDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.accountobject_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)
