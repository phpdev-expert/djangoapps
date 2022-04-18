# modify all the variables in settings.py.
# This file is exec'd from settings.py, so it has access to and can

DEBUG = True
SITE_TITLE="GDR USER PANEL"
# Make these unique, and don't share it with anybody.
SECRET_KEY = ")qy^^-^dhnqix_mn2r4umq^c(s#im7dn1@2)6e!&z^%kn4j#-a"
NEVERCACHE_KEY = "kepb_es#65ps9-o5b+z3-i8em8yl5k2c4fr@k92cib56r=j*mo"

import keyring
import getpass
database_name = 'db_mezz_db'
username = 'db_user_mezz'
mezzpassword = keyring.get_password(database_name, username)

while mezzpassword == None :
    mezzpassword = getpass.getpass(database_name + " Password:\n")
    # store the password
    keyring.set_password(database_name, username, mezzpassword)



DATABASES = {
    "default": {
         "ENGINE": "django.db.backends.postgresql_psycopg2",
         "NAME": "gdr_mezz",
         'USER': 'matt',
         'PASSWORD':mezzpassword,
         'HOST':'127.0.0.1',
         'PORT': '5432'
    },
    "grd_db": {
         "ENGINE": "django.db.backends.postgresql_psycopg2",
         "NAME": "grd_db",
         'OPTIONS' : {
                'options': '-c search_path=gdr'
            },
         'USER': 'matt',
         'PASSWORD':mezzpassword,
         'HOST':'127.0.0.1',
         'PORT': '5432'
    }

}

# Allowed development hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1"]

###################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

# FABRIC = {
#     "DEPLOY_TOOL": "rsync",  # Deploy with "git", "hg", or "rsync"
#     "SSH_USER": "",  # VPS SSH username
#     "HOSTS": [""],  # The IP address of your VPS
#     "DOMAINS": [""],  # Will be used as ALLOWED_HOSTS in production
#     "REQUIREMENTS_PATH": "requirements.txt",  # Project's pip requirements
#     "LOCALE": "en_US.UTF-8",  # Should end with ".UTF-8"
#     "DB_PASS": "",  # Live database password
#     "ADMIN_PASS": "",  # Live admin user password
#     "SECRET_KEY": SECRET_KEY,
#     "NEVERCACHE_KEY": NEVERCACHE_KEY,
# }
AUTH_USER_MODEL = "managements.AdminUsers"
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length':8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {'NAME': 'managements.validators.NumberValidator', },
    {'NAME': 'managements.validators.UserNameValidator', },
    {'NAME': 'managements.validators.UserNameAlphaValidate', },
    {'NAME': 'managements.validators.LastPasswordsValidate', },




]
