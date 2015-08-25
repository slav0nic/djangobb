#!/usr/bin/env python
import sys
import os
from os.path import dirname, abspath
from optparse import OptionParser

import django
from django.conf import settings, global_settings

# For convenience configure settings if they are not pre-configured or if we
# haven't been provided settings to use by environment variable.
if not settings.configured and not os.environ.get('DJANGO_SETTINGS_MODULE'):
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        STATIC_ROOT='static/',
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.sitemaps',
            'django.contrib.humanize',

            'haystack',
            'pagination',

            'djangobb_forum',
        ),
        MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
                'django.middleware.locale.LocaleMiddleware',
                'pagination.middleware.PaginationMiddleware',
                'django.middleware.transaction.TransactionMiddleware',
                'djangobb_forum.middleware.LastLoginMiddleware',
                'djangobb_forum.middleware.UsersOnline',
        ),
        TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
            'djangobb_forum.context_processors.forum_settings',
        ),
        PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',),
        ROOT_URLCONF='djangobb_forum.tests.urls',
        DEBUG=False,
        SITE_ID=1,
        HAYSTACK_CONNECTIONS = {
            'default': {
                'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'
            }
        }
    )
    if django.VERSION[:2] >= (1, 7):
        django.setup()

from django.test.runner import DiscoverRunner

def runtests(*test_args, **kwargs):
    # TODO: remove after drop django 1.6 support
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['djangobb_forum']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    test_runner = DiscoverRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)
