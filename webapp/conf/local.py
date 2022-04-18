from django.utils import timezone
from webapp.conf.base import *
from kombu.common import Broadcast
from kombu import Exchange
from kombu import Queue

SERVER = "dev"
ENVIRONMENT = "local"
DEBUG = True
# SILKY_PYTHON_PROFILER = False
#
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "ab_reporting_v3",
        "USER": "postgres",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "5432",
    },
}
# DATABASES = {
#             'default': {
#                         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#                         'NAME': 'smb2_reporting',
#                         'USER': 'Analyze',
#                         'PASSWORD': 'Rmn_Anlz3_5264#',
#                         'HOST': 'roman3-analyze-dev.c7do6oljmfzz.eu-west-2.rds.amazonaws.com',
#                 'PORT': '5432',
#             },
#
#             }


LANGUAGE_CODE = "en-us"

AWS_S3_ACCESS_KEY_ID = "AKIAIONNVLHF2R4I3T6Q"
AWS_S3_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "webapp"
AWS_S3_HOST = "s3.ap-south-1.amazonaws.com"

SECRET_KEY = "i5f11qvno%lhb%^rpr&u%yr#vg@s1pc82tt*i_!c)762ln&wk%"

CELERY_BROKER_URL = "amqp://guest@localhost"
# CELERY_BROKER_URL = "amqp://gtlumjvy:Yf9OPQkj-9ssttfiWxFfTQ0Qn4oOOCti@ambitious-dingo.rmq.cloudamqp.com/gtlumjvy"  # noqa E501

# CELERY_BROKER_URL = "amqp://cwignoqf:beq3omwiy20nlnkly7uekzzcjtjnhuyg@lionfish.rmq.cloudamqp.com/cwignoqf" # noqa E501
# CELERY_BROKER_URL = "amqp://ebicwaqc:tnatlrroah6mktucwwhb6u-uuxkwucnu@prawn.rmq.cloudamqp.com/ebicwaqc"


# Queues
LINKEDIN_QUEUE = "linkedin_queue"
TWITTER_ACCOUNT_QUEUE = "twitter_queue"
FACEBOOK_QUEUE = "facebook_queue"
INSTAGRAM_QUEUE = "instagram_queue"
USER_QUEUE = "user_queue"
FACEBOOK_SYNC_QUEUE = "facebook_sync_queue"
FACEBOOK_DELETE_QUEUE = "facebook_delete_queue"
INSTAGRAM_SYNC_QUEUE = "instagram_sync_queue"
LINKEDIN_SYNC_QUEUE = "linkedin_sync_queue"
TWITTER_SYNC_QUEUE = "twitter_sync_queue"
# FACEBOOK_POST_QUEUE = 'facebook_posts'
# FACEBOOK_ERROR_QUEUE = 'facebook_errors'
# TWITTER_POST_QUEUE = 'twitter_posts'
# TWITTER_ERROR_QUEUE = 'twitter_errors'
# LINKEDIN_POST_QUEUE = 'linkedin_posts'
# LINKEDIN_ERROR_QUEUE = 'linkedin_errors'
TASK_QUEUE = "default_queue"

CELERY_ROUTES = {
    DELETE_USER_TASK: {"queue": USER_QUEUE},
    LINKEDIN_PAGE_SYNC_TASK: {"queue": LINKEDIN_QUEUE},
    LINKEDIN_ACCOUNT_DELETE_TASK: {"queue": LINKEDIN_QUEUE},
    LINKEDIN_PAGE_DELETE_TASK: {"queue": LINKEDIN_QUEUE},
    # SYNC_PAGE_ANALYTICS: {"queue": LINKEDIN_QUEUE},
    LINKEDIN_SYNC_POST_ANALYTICS: {"queue": LINKEDIN_QUEUE},
    LINKEDIN_PAGE_SYNC_ACTION_TASK: {"queue": LINKEDIN_SYNC_QUEUE},
    TWITTER_ACCOUNT_SYNC_TASK: {"queue": TWITTER_ACCOUNT_QUEUE},
    TWITTER_ACCOUNT_DELETE_TASK: {"queue": TWITTER_ACCOUNT_QUEUE},
    TWITTER_ACCOUNT_SYNC_ACTION_TASK: {"queue": TWITTER_SYNC_QUEUE},
    FACEBOOK_PAGE_SYNC_TASK: {"queue": FACEBOOK_QUEUE},
    FACEBOOK_PAGE_POST_SYNC_TASK: {"queue": FACEBOOK_QUEUE},
    FACEBOOK_PAGE_VIDEO_SYNC_TASK: {"queue": FACEBOOK_QUEUE},
    FACEBOOK_PAGE_DELETE_TASK: {"queue": FACEBOOK_QUEUE},
    FACEBOOK_PAGE_SYNC_ACTION_TASK: {"queue": FACEBOOK_SYNC_QUEUE},
    FACEBOOK_PAGE_DELETE_ACTION_TASK: {"queue": FACEBOOK_DELETE_QUEUE},
    FACEBOOK_GROUP_DELETE_TASK: {"queue": FACEBOOK_QUEUE},
    INSTAGRAM_ACCOUNT_SYNC_TASK: {"queue": INSTAGRAM_QUEUE},
    INSTAGRAM_ACCOUNT_DELETE_TASK: {"queue": INSTAGRAM_QUEUE},
    INSTAGRAM_BUSINESS_ACCOUNT_SYNC_TASK: {"queue": INSTAGRAM_QUEUE},
    INSTAGRAM_BUSINESS_ACCOUNT_DELETE_TASK: {"queue": INSTAGRAM_QUEUE},
    INSTAGRAM_SYNC_ACTION_TASK: {"queue": INSTAGRAM_SYNC_QUEUE},
    #     PUBLISH_FACEBOOK_PAGE_POST_TASK: {
    #         'queue': FACEBOOK_POST_QUEUE
    #     },
    #     PUBLISH_FACEBOOK_GROUP_POST_TASK: {
    #         'queue': FACEBOOK_POST_QUEUE
    #     },
    #     PUBLISH_TWITTER_TASK: {
    #         'queue': TWITTER_POST_QUEUE
    #     },
    #     PUBLISH_LINKEDIN_TASK: {
    #         'queue': LINKEDIN_POST_QUEUE
    #     },
}

# Celery Queues
CELERY_QUEUES = (
    Broadcast(name=USER_QUEUE, exchange=Exchange(USER_QUEUE, type="fanout")),
    Broadcast(name=LINKEDIN_QUEUE, exchange=Exchange(LINKEDIN_QUEUE, type="fanout")),
    Broadcast(
        TWITTER_ACCOUNT_QUEUE, exchange=Exchange(TWITTER_ACCOUNT_QUEUE, type="fanout")
    ),
    Broadcast(FACEBOOK_QUEUE, exchange=Exchange(FACEBOOK_QUEUE, type="fanout")),
    Broadcast(INSTAGRAM_QUEUE, exchange=Exchange(INSTAGRAM_QUEUE, type="fanout")),
    Queue(TASK_QUEUE, routing_key=TASK_QUEUE, exchange=Exchange(TASK_QUEUE)),
    Queue(
        FACEBOOK_SYNC_QUEUE,
        routing_key=FACEBOOK_SYNC_QUEUE,
        exchange=Exchange(FACEBOOK_SYNC_QUEUE),
    ),
    Queue(
        FACEBOOK_DELETE_QUEUE,
        routing_key=FACEBOOK_DELETE_QUEUE,
        exchange=Exchange(FACEBOOK_DELETE_QUEUE),
    ),
    Queue(
        INSTAGRAM_SYNC_QUEUE,
        routing_key=INSTAGRAM_SYNC_QUEUE,
        exchange=Exchange(INSTAGRAM_SYNC_QUEUE),
    ),
    Queue(
        LINKEDIN_SYNC_QUEUE,
        routing_key=LINKEDIN_SYNC_QUEUE,
        exchange=Exchange(LINKEDIN_SYNC_QUEUE),
    ),
Queue(
        TWITTER_SYNC_QUEUE,
        routing_key=TWITTER_SYNC_QUEUE,
        exchange=Exchange(TWITTER_SYNC_QUEUE),
    ),
)
