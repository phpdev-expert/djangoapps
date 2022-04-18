from django.core.management.base import BaseCommand

from webapp.apps.metrics.data_loader.linkedin import LinkedinDataLoader
from webapp.apps.metrics.data_loader.facebook import FacebookDataLoader
from webapp.apps.metrics.data_loader.instagram import InstagramDataLoader
from webapp.apps.metrics.tasks.crontasks import test
from webapp.apps.metrics.tasks.facebook import delete_facebook_page
from webapp.apps.metrics.tasks.instagram import instagram_sync_task
# from webapp.apps.metrics.tasks import fetch_page_metrics_task, fetch_page_post_metrics_task
from webapp.apps.metrics.data_loader.twitter import TwitterDataLoader
from webapp.apps.metrics.tasks import linkedin_saved_task, twitter_sync_task, facebook_sync_task, fetch_metrics_task
from webapp.apps.metrics.tasks.linkedin import delete_linkedin_page
from webapp.apps.metrics.tasks.twitter import delete_twitter_account


class Command(BaseCommand):
    help = "Fetch all metrics for a page"

    def add_arguments(self, parser):
        parser.add_argument("page_type", nargs="+", type=str)
        parser.add_argument("page_id", nargs="+", type=str)

    def handle(self, *args, **options):
        # metrics = fetch_page_metrics_task.delay(options['page_type'][0], options['page_id'][0])
        # posts = fetch_page_post_metrics_task.delay(options['page_type'][0], options['page_id'][0])
        #
        # self.stdout.write(self.style.SUCCESS('Started... '))

        page_type = options["page_type"][0]
        page_id = options["page_id"][0]

        if page_type == "linkedin":
            # page_id = "13406193"
            linkedin_data = {
                "auth_user_id": 2,
                "page_id": page_id,
                "name": "Norah Ai",
                "access_token": "AQXhuW1TdzvUGGVtc-GBIvHdCHn4uq2JYEuD0n2LoWX_bDIiNdBTFhhwQadY5iVsMHACYQZ8rlhZYUptZwldVWRIkezC0AMc9vnrknsQB7KHkfN1kP6nUJvxyDgveC06R6BPz_O9liLsr5dfUVzWaR-XGsKaYa_bnTA_OAMTGe8jbVmtS9B4QvPVWDEvYHHS1vs557ooyaSOxpCUb4KxwWQEAT35stPI1zO7Aqp8qAaVKeDbOsOUr5VwLvDxzum-OW8R38esF2w9TUIdkylPebKek-NNrW42qLUcidqISxIHAxpaWs4eMa-8Opn5NcB5KkYCxgqvSytB4PniqO-itwKbeUdaMQ",  # noqa E501
                "status": "active",
                "description": "A team of professional gamers at heart and data scientists in our minds is what defines us. \r\nOur dream of becoming the largest provider of cutting edge technology to gaming studios across \r\nthe globe is what keeps us up at night. Reach out to us if your passion is gaming as \r\nwe are here to help you in the journey from inception till beyond .",  # noqa E501
            }
            linkedin_saved_task(data=linkedin_data)
            # delete_linkedin_page(data=linkedin_data)
            # obj.fetch_and_save_page_analytics()

        elif page_type == "facebook":
            facebook_data = {
                'auth_user_id': 1,
                'page_id': page_id,
                'status': 'active'
            }

            facebook_data = {
                'name': "Tata AIG",
                'page_id': '579358065547552',
                'social_account': 99,
                'phone': None,
                'website': None,
                'about': '',
                'description': '',
                'cover_url': None,
                'picture_url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/cp0/p50x50/85038594_107973467449758_5874320216342659072_o.png?_nc_cat=104&_nc_sid=dbb9e7&_nc_ohc=2ArKAy lEcY8AX8Ia1Qn&_nc_ht=scontent.xx&oh=e008a20302e6e852c6b5062a2dda3314&oe=5EA5693D',
                'access_token': 'sEAAFNUMclxHIBADNZCSQJDaqK7Yxpl88ZBF190pE9ve7kiNbbWqIvLQe3p6nVI7cRG42g8ZAeJfnIg4aWLkLmcmgt8IGkmo3ZAmGLaQgC48KmEj1USO2px7Bhn0v1gRcMYBiBvugNz23MmZA757Jjg1GZCsRZADXocDHm2TyGMjyXAZDZD',
                'status': 'active',
                'auth_user_id': 1
            }
            # facebook_sync_task(data=facebook_data)
            delete_facebook_page(data=facebook_data)
            # obj = FacebookDataLoader(user_id=1, page_id=page_id)
            # obj.fetch_insights({})
        elif page_type == "instagram":
            # 17841400794376360

            instagram_data = {
            'social_account_id': '17841415203417539',
             'access_token': 'IGQVJYb1pQNTl6c3NhMVF6U2VVLXkyMjZAvZAjN6OWlESEZA0VXpxSzFKRWpZAZA0NaZA0s2U25Jb2lLRUpnc2tmQjVTcG5iVm9SdFAydzR3WVlYcC1kV0xfR3pqQlloT0hKUWxDOEMyYUgxcnpOS2hJWnh5XzRlQW1tdl94bFFj',
             'access_token_secret': '',
             'first_name': '',
             'last_name': '',
             'screen_name': 'pyxispv',
             'email': '',
             'auth_user_id': 83,
             'account_type': 'BUSINESS',
             'status': 'active'
             }
            instagram_data = {
                'auth_user_id': 1,
                'social_account_id': page_id,
                "screen_name": "yes_bank",
                "access_token": "EAAFNUMclxHIBAJHyyXqOiJEXrWlTiVso2IaSEaJOygdMoe9XZCZCxGQw1vaLQkuT0IMZC0ALP1SbClbLsJffhtZBWGMKuRl6T9txDXklBQQDHL86YCVqNU8Rdql6VMENRUW3SA1tDTg4AMCaTzyPF15XkmJkat16i7XmlcJjlz8Hi4qVudMS",
                'status': 'active'
            }
            instagram_sync_task(data=instagram_data)
            # obj = InstagramDataLoader(user_id=1, page_id=page_id)
            # obj.fetch_insights({})

        elif page_type == "twitter":
            # 1073889170320351233
            twitter_data = {
                'social_account_id': page_id,
                'access_token': '1073889170320351233-TLXYTA0ygy1wVqWbgfWL7zBat24XYA',
                'access_token_secret': 'iF2m0flciIE8Ij7w7ZEbRPg12UruuEQvJrX4GxIaFThLg',
                'first_name': 'PmPyxis',
                'last_name': '',
                'screen_name': 'PmPyxis',
                'email': '',
                'auth_user_id': 2,
                'account_type': '',
                'status': 'active'
            }
            twitter_sync_task(data=twitter_data)
            # delete_twitter_account(data=twitter_data)
            # obj = TwitterDataLoader(user_id=twitter_data['auth_user_id'], page_id=page_id)
            # obj.fetch_metrics(data=twitter_data)
            # obj.fetch_post()
            # obj.fetch_messages()
            # obj.fetch_account_insights()
