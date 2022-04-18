from django.core.mail import send_mail
from django.conf import settings
from django.http import BadHeaderError, HttpResponse, HttpResponseRedirect
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from django.core.mail import send_mail, EmailMessage
from email import encoders
import os
from recruit_api.settings.email_server import EMAIL_HOST_USER


class EmailServer:

    def send(self, subject, message, recipients, uploaded_file):

        email = EmailMessage(
            subject,
            message,
            EMAIL_HOST_USER,
            recipients,
        )

        if uploaded_file:
            email.attach_file(settings.MEDIA_ROOT+str(uploaded_file))

        if email:
            try:
                return email.send()
            except BadHeaderError:
                return "Invalid header found."

        # return send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)
