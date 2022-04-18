# coding=utf-8
"""
Middleware for handling exceptions
"""
import json
import logging
import traceback

from django.http import HttpResponse
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class ExceptionMiddleWare(object):
    """
    Exception middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Process Exception
        :param request:
        :param exception:
        :return:
        """
        logger.info("request.path " + request.path)
        logger.error("error: " + traceback.format_exc())
        return self.handle_exception(request, exception)

    def handle_exception(self, request, exception):
        """
        Handle Exception
        :param request:
        :param exception:
        :return:
        """
        response = dict()
        logger.exception(exception)
        response["error"] = True
        response["message"] = (
            exception.message if hasattr(exception, "message") else str(exception)
        )
        response["code"] = exception.code if hasattr(exception, "code") else "101"
        return HttpResponse(json.dumps(response), content_type="application/json")


def rest_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    logger.exception(exc)
    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    return response
