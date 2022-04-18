# -*- coding: utf-8 -*-

"""
BAseAPIView by Overriding default APIView
"""
import logging

from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView


from webapp.base.constants import POST_METRIC_FORMAT
from webapp.base.utils import generate_metric_value

logger = logging.getLogger(__name__)


class BaseAPIView(APIView):
    """
    Overriding default APIView
    """

    validation_serializer = None

    def dispatch(self, *args, **kwargs):
        """
        Overriding APIView's dispatch
        """
        request = args[0]
        user_details = request.user_details
        if user_details:
            logger.debug(f"User Info - {user_details}")
            request.auth_user_id = request.user_details.get("id")
            if not request.auth_user_id:
                raise Exception("Invalid token")
        else:
            raise Exception("User not found")
        if request.method == "GET":
            data = request.GET
        else:
            data = request.POST
        if settings.LOG_REQUEST:
            logger.info("request= %s" % data)
        if self.validation_serializer:
            self.request_data = self.validation_serializer(data=data)
            try:
                self.request_data.is_valid(raise_exception=True)
            except ValidationError as e:
                for k, v in e.detail.items():
                    message = "%s - %s" % (k, v[0])
                    raise Exception(message)
        return super(BaseAPIView, self).dispatch(*args, **kwargs)
