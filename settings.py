# -*- coding: utf-8 -*-
import os.path

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'DjangoBB'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Kiew'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qry+e%=0&2c(k$=+czmsv8sw74ci5*m8t$83cv!#72b9)ge%io'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.account.middleware.AuthKeyMiddleware',
    'apps.forum.middleware.LastLoginMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'apps.account',
    'apps.captcha',
    'apps.forum',
)

FORCE_SCRIPT_NAME = ''

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

# Account settings
ACCOUNT_ACTIVATION = False
LOGIN_REDIRECT_URL = '/forum'
ACCOUNT_CAPTCHA = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH = 2
LOGIN_URL = '/forum/account/login/'
ACCOUNT_DOMAIN = '/forum/account/'
ACCOUNT_AUTH_KEY_TIMEOUT = 60 * 60 * 24

# FORUM settings
FORUM_ADMIN_EMAIL = 'alafin@python.su'
FORUM_TOPIC_PAGE_SIZE = 10
FORUM_FORUM_PAGE_SIZE = 20
FORUM_USERS_PAGE_SIZE = 20
FORUM_AVATARS_UPLOAD_TO = 'forum/avatars'
FORUM_AVATAR_WIDTH = 100
FORUM_AVATAR_HEIGHT = 100
FORUM_DEFAULT_TIME_ZONE = 3
FORUM_SIGNATURE_MAX_LENGTH = 1024
FORUM_SIGNATURE_MAX_LINES = 3
#FORUM_QUICK_TOPICS_NUMBER = 10
#FORUM_QUICK_POSTS_NUMBER = 10
FORUM_READ_TIMEOUT = 3600 * 24 * 7
FORUM_HEADER = 'DjangoBB'
FORUM_TAGLINE = 'Django based forum engine'
FORUM_DEFAULT_MARKUP = 'bbcode'
FORUM_NOTICE = ''
FORUM_HOST = 'localhost:8000'
FORUM_USER_ONLINE_TIMEOUT = 30
# Stars
FORUM_STAR_0 = 0
FORUM_STAR_0_HALF = 10
FORUM_STAR_1 = 25
FORUM_STAR_1_HALF = 50
FORUM_STAR_2 = 75
FORUM_STAR_2_HALF = 100
FORUM_STAR_3 = 150
FORUM_STAR_3_HALF = 200
FORUM_STAR_4 = 300
FORUM_STAR_4_HALF = 500
FORUM_STAR_5 = 1000
# Smiles
FORUM_EMOTION_SMILE = '<img src="%sforum/img/smilies/smile.png">' % MEDIA_URL
FORUM_EMOTION_NEUTRAL = '<img src="%sforum/img/smilies/neutral.png">' % MEDIA_URL
FORUM_EMOTION_SAD = '<img src="%sforum/img/smilies/sad.png">' % MEDIA_URL
FORUM_EMOTION_BIG_SMILE = '<img src="%sforum/img/smilies/big_smile.png">' % MEDIA_URL
FORUM_EMOTION_YIKES = '<img src="%sforum/img/smilies/yikes.png">' % MEDIA_URL
FORUM_EMOTION_WINK = '<img src="%sforum/img/smilies/wink.png">' % MEDIA_URL
FORUM_EMOTION_HMM = '<img src="%sforum/img/smilies/hmm.png">' % MEDIA_URL
FORUM_EMOTION_TONGUE = '<img src="%sforum/img/smilies/tongue.png">' % MEDIA_URL
FORUM_EMOTION_LOL = '<img src="%sforum/img/smilies/lol.png">' % MEDIA_URL
FORUM_EMOTION_MAD = '<img src="%sforum/img/smilies/mad.png">' % MEDIA_URL
FORUM_EMOTION_ROLL = '<img src="%sforum/img/smilies/roll.png">' % MEDIA_URL
FORUM_EMOTION_COOL = '<img src="%sforum/img/smilies/cool.png">' % MEDIA_URL

try:
    from local_settings import *
except ImportError:
    pass