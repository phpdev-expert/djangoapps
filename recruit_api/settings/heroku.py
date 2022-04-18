import os
if os.environ['ENV_NAME'] == 'prod':
    import django_heroku
    django_heroku.settings(locals())
