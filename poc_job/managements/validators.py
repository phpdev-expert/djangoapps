import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from managements.models import LastPasswords
from django.conf import settings
import hashlib


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )

class UserNameValidator(object):
    def validate(self, password, user=None):
        if password==user.username:
            raise ValidationError(
                _("Password cannot be the same as username."),
                code='password_as_username',
            )

    def get_help_text(self):
        return _(
            "Password cannot be the same as username."
        )

class UserNameAlphaValidate(object):
    def validate(self, password, user=None):
        if not password[0].isalpha():
            raise ValidationError(
                _("Password must start with an alphabetic character."),
                code='password_as_alpha',
            )

    def get_help_text(self):
        return _(
            "Password must start with an alphabetic character."
        )

class LastPasswordsValidate(object):
    def validate(self, password, user=None):
        lastp=settings.PREVOIUS_PASSWORDS
        result = hashlib.md5(password.encode())
        new_password=result.hexdigest()
        lps=LastPasswords.objects.filter(user_id=user.pk).all()[:lastp][::-1]
        prentme=False
        for lp in lps:
            if lp.last_passwords==new_password:
                prentme=True
        if prentme:
            raise ValidationError(
                _("Can not use old password."),
                code='password_as_alpha',
            )
    def get_help_text(self):
        return _(
            "Can not use last  passwords ."
        )
