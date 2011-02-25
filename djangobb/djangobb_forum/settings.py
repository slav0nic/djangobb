# -*- coding: utf-8 -*-
from django.conf import settings
import re

def get(key, default):
    return getattr(settings, key, default)

# FORUM Settings
FORUM_BASE_TITLE = get('DJANGOBB_FORUM_BASE_TITLE', 'Django Bulletin Board')
FORUM_META_DESCRIPTION = get('DJANGOBB_FORUM_META_DESCRIPTION', '')
FORUM_META_KEYWORDS = get('DJANGOBB_FORUM_META_KEYWORDS', '')
TOPIC_PAGE_SIZE = get('DJANGOBB_TOPIC_PAGE_SIZE', 10)
FORUM_PAGE_SIZE = get('DJANGOBB_FORUM_PAGE_SIZE', 20)
SEARCH_PAGE_SIZE = get('DJANGOBB_SEARCH_PAGE_SIZE', 20)
USERS_PAGE_SIZE = get('DJANGOBB_USERS_PAGE_SIZE', 20)
AVATARS_UPLOAD_TO = get('DJANGOBB_AVATARS_UPLOAD_TO', 'forum/avatars')
AVATAR_WIDTH = get('DJANGOBB_AVATAR_WIDTH', 60)
AVATAR_HEIGHT = get('DJANGOBB_AVATAR_HEIGHT', 60)
DEFAULT_TIME_ZONE = get('DJANGOBB_DEFAULT_TIME_ZONE', 3)
SIGNATURE_MAX_LENGTH = get('DJANGOBB_SIGNATURE_MAX_LENGTH', 1024)
SIGNATURE_MAX_LINES = get('DJANGOBB_SIGNATURE_MAX_LINES', 3)
READ_TIMEOUT = get('DJANGOBB_READ_TIMEOUT', 3600 * 24 * 7)
HEADER = get('DJANGOBB_HEADER', 'DjangoBB')
TAGLINE = get('DJANGOBB_TAGLINE', 'Django based forum engine')
DEFAULT_MARKUP = get('DJANGOBB_DEFAULT_MARKUP', 'bbcode')
NOTICE = get('DJANGOBB_NOTICE', '')
USER_ONLINE_TIMEOUT = get('DJANGOBB_USER_ONLINE_TIMEOUT', 15)
EMAIL_DEBUG = get('DJANGOBB_FORUM_EMAIL_DEBUG', False)
POST_USER_SEARCH = get('DJANGOBB_POST_USER_SEARCH', 1)

# GRAVATAR Extension
GRAVATAR_SUPPORT = get('DJANGOBB_GRAVATAR_SUPPORT', True)
GRAVATAR_DEFAULT = get('DJANGOBB_GRAVATAR_DEFAULT', 'identicon')

# LOFI Extension
LOFI_SUPPORT = get('DJANGOBB_LOFI_SUPPORT', True)

# PM Extension
PM_SUPPORT = get('DJANGOBB_PM_SUPPORT', True)

# AUTHORITY Extension
AUTHORITY_SUPPORT = get('DJANGOBB_AUTHORITY_SUPPORT', True)
AUTHORITY_STEP_0 = get('DJANGOBB_AUTHORITY_STEP_0', 0)
AUTHORITY_STEP_1 = get('DJANGOBB_AUTHORITY_STEP_1', 10)
AUTHORITY_STEP_2 = get('DJANGOBB_AUTHORITY_STEP_2', 25)
AUTHORITY_STEP_3 = get('DJANGOBB_AUTHORITY_STEP_3', 50)
AUTHORITY_STEP_4 = get('DJANGOBB_AUTHORITY_STEP_4', 75)
AUTHORITY_STEP_5 = get('DJANGOBB_AUTHORITY_STEP_5', 100)
AUTHORITY_STEP_6 = get('DJANGOBB_AUTHORITY_STEP_6', 150)
AUTHORITY_STEP_7 = get('DJANGOBB_AUTHORITY_STEP_7', 200)
AUTHORITY_STEP_8 = get('DJANGOBB_AUTHORITY_STEP_8', 300)
AUTHORITY_STEP_9 = get('DJANGOBB_AUTHORITY_STEP_9', 500)
AUTHORITY_STEP_10 = get('DJANGOBB_AUTHORITY_STEP_10', 1000)

# REPUTATION Extension
REPUTATION_SUPPORT = get('DJANGOBB_REPUTATION_SUPPORT', True)

# ATTACHMENT Extension
ATTACHMENT_SUPPORT = get('DJANGOBB_ATTACHMENT_SUPPORT', True)
ATTACHMENT_UPLOAD_TO = get('DJANGOBB_ATTACHMENT_UPLOAD_TO', 'forum/attachments')
ATTACHMENT_SIZE_LIMIT = get('DJANGOBB_ATTACHMENT_SIZE_LIMIT', 1024 * 1024)

# SMILE Extension
SMILES_SUPPORT = get('DJANGOBB_SMILES_SUPPORT', True)
EMOTION_SMILE = get('DJANGOBB_EMOTION_SMILE', '<img src="%sforum/img/smilies/smile.png" />' % settings.MEDIA_URL)
EMOTION_NEUTRAL = get('DJANGOBB_EMOTION_NEUTRAL', '<img src="%sforum/img/smilies/neutral.png" />' % settings.MEDIA_URL)
EMOTION_SAD = get('DJANGOBB_EMOTION_SAD', '<img src="%sforum/img/smilies/sad.png" />' % settings.MEDIA_URL)
EMOTION_BIG_SMILE = get('DJANGOBB_EMOTION_BIG_SMILE', '<img src="%sforum/img/smilies/big_smile.png" />' % settings.MEDIA_URL)
EMOTION_YIKES = get('DJANGOBB_EMOTION_YIKES', '<img src="%sforum/img/smilies/yikes.png" />' % settings.MEDIA_URL)
EMOTION_WINK = get('DJANGOBB_EMOTION_WINK', '<img src="%sforum/img/smilies/wink.png" />' % settings.MEDIA_URL)
EMOTION_HMM = get('DJANGOBB_EMOTION_HMM', '<img src="%sforum/img/smilies/hmm.png" />' % settings.MEDIA_URL)
EMOTION_TONGUE = get('DJANGOBB_EMOTION_TONGUE', '<img src="%sforum/img/smilies/tongue.png" />' % settings.MEDIA_URL)
EMOTION_LOL = get('DJANGOBB_EMOTION_LOL', '<img src="%sforum/img/smilies/lol.png" />' % settings.MEDIA_URL)
EMOTION_MAD = get('DJANGOBB_EMOTION_MAD', '<img src="%sforum/img/smilies/mad.png" />' % settings.MEDIA_URL)
EMOTION_ROLL = get('DJANGOBB_EMOTION_ROLL', '<img src="%sforum/img/smilies/roll.png" />' % settings.MEDIA_URL)
EMOTION_COOL = get('DJANGOBB_EMOTION_COOL', '<img src="%sforum/img/smilies/cool.png" />' % settings.MEDIA_URL)
SMILES = ((r'(:|=)\)', EMOTION_SMILE), #:), =)
          (r'(:|=)\|',  EMOTION_NEUTRAL), #:|, =| 
          (r'(:|=)\(', EMOTION_SAD), #:(, =(
          (r'(:|=)D', EMOTION_BIG_SMILE), #:D, =D
          (r':o', EMOTION_YIKES), # :o, :O
          (r';\)', EMOTION_WINK), # ;\ 
          (r':/', EMOTION_HMM), #:/
          (r':P', EMOTION_TONGUE), # :P
          (r':lol:', EMOTION_LOL),
          (r':mad:', EMOTION_MAD),
          (r':rolleyes:', EMOTION_ROLL),
          (r':cool:', EMOTION_COOL)
         )
SMILES = get('DJANGOBB_SMILES', SMILES)