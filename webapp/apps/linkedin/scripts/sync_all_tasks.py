from webapp.apps.linkedin.tasks import get_page_analytics, get_post_analytics, get_page_follower, get_shares, \
    get_page_analytics_by_date

URN = "urn:li:organization:13406193"


def sync_all(access_token, auth_id=None):
    get_page_analytics.delay(access_token=access_token, auth_id=auth_id, page_urn=URN)
    get_shares.delay(access_token=access_token, page_urn=URN)
    # get_page_analytics_by_date(access_token=access_token, page_urn=URN)