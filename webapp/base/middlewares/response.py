# coding=utf-8
"""
Response Middleware
"""
import json
import logging

from django.conf import settings
from django.http import HttpResponse

from webapp.base.encoders import LazyEncoder

logger = logging.getLogger(__name__)


class ResponseMiddleWare(object):
    """
    Response Middleware Class
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        data = self.get_response(request)

        if (
            "json" not in data._headers["content-type"][1]
            or "docs/?format=openapi" in request.build_absolute_uri()
        ):
            return data
        if not hasattr(data, "data"):
            return data
        response = dict()
        if data.status_code >= 400:

            response["error"] = True
        else:
            response["error"] = False
        response["data"] = data.data
        response = json.dumps(response, cls=LazyEncoder)
        if settings.LOG_RESPONSE:
            logger.info("response = %s" % response)
        return HttpResponse(
            response,
            content_type=data._headers["content-type"][1],
            status=data.status_code,
        )
