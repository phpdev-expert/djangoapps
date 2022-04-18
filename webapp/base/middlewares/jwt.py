# coding=utf-8
"""
Request Middleware
"""
import logging

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)
log = logging.getLogger("webapp")


class JWTMiddleWare(object):
    """
    Request Middleware Class
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        """
        Middleware for logging request
        :param request:
        :return:
        """
        request.user_details = None
        user_token = request.META.get("HTTP_TOKEN")
        if user_token:
            logger.info("User Token "+ user_token)
            log.info("User Token "+user_token)
            try:
                request.user_details = jwt.decode(
                    user_token, settings.JWT_SECRET, algorithms=["HS256"]
                )
                # request.user_details = {"id": 1}
            except Exception as exc:
                logger.exception(str(exc))
