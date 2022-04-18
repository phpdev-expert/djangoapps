# coding=utf-8
"""
Request Middleware
"""
import logging
import ast

logger = logging.getLogger(__name__)


class RequestMiddleWare(object):
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
        request.page_ids = []
        page_ids = request.GET.get("pageid", False)
        if not page_ids:
            page_ids = request.META.get("HTTP_PAGEID")
        if page_ids:
            page_ids = ast.literal_eval(page_ids)
            request.page_ids = [page_ids] if type(page_ids) == int else page_ids

        logger.info(request.get_full_path)
