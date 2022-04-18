from django.conf import settings
import requests


def api_connect(url, access_token, data=None, params=None):
    """
    Base LinkedIn API Connect
    :param url:
    :param access_token:
    :param data:
    :param method:
    :return:
    """
    URL = settings.LINKEDIN_BASE_URL + url
    headers = {
        "Authorization": f"Bearer {access_token}",
        # "cache-control": "no-cache",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    if data:
        response = requests.post(url=URL, headers=headers, data=data)
    if params:
        response = requests.get(url=URL, headers=headers, params=params)
    else:
        response = requests.request('get', url=URL, headers=headers)

    return response


class DuplicateKey(object):
    def __init__(self, name):
        self.name = name

    # As it would print for a user
    def __str__(self):
        return self.name

    # As it would print for a debugging person
    def __repr__(self):
        return "'" + self.name + "'"
