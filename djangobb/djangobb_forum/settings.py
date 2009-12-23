from django.conf import settings
import re

def get(key, default):
    return getattr(settings, key, default)

# FORUM Settings
FORUM_BASE_TITLE = get('FORUM_BASE_TITLE', 'Django Bulletin Board')
FORUM_META_DESCRIPTION = get('FORUM_META_DESCRIPTION', '')
FORUM_META_KEYWORDS = get('FORUM_META_KEYWORDS', '')
TOPIC_PAGE_SIZE = get('TOPIC_PAGE_SIZE', 10)
FORUM_PAGE_SIZE = get('FORUM_PAGE_SIZE', 20)
SEARCH_PAGE_SIZE = get('SEARCH_PAGE_SIZE', 20)
USERS_PAGE_SIZE = get('USERS_PAGE_SIZE', 20)
AVATARS_UPLOAD_TO = get('AVATARS_UPLOAD_TO', 'forum/avatars')
AVATAR_WIDTH = get('AVATAR_WIDTH', 60)
AVATAR_HEIGHT = get('AVATAR_HEIGHT', 60)
DEFAULT_TIME_ZONE = get('DEFAULT_TIME_ZONE', 3)
SIGNATURE_MAX_LENGTH = get('SIGNATURE_MAX_LENGTH', 1024)
SIGNATURE_MAX_LINES = get('SIGNATURE_MAX_LINES', 3)
READ_TIMEOUT = get('READ_TIMEOUT', 3600 * 24 * 7)
HEADER = get('HEADER', 'DjangoBB')
TAGLINE = get('TAGLINE', 'Django based forum engine')
DEFAULT_MARKUP = get('DEFAULT_MARKUP', 'bbcode')
NOTICE = get('NOTICE', '')
HOST = get('HOST', 'localhost:8000')
USER_ONLINE_TIMEOUT = get('USER_ONLINE_TIMEOUT', 15)
EMAIL_DEBUG = get('FORUM_EMAIL_DEBUG', False)
POST_USER_SEARCH = get('POST_USER_SEARCH', 1)

# GRAVATAR Extension
GRAVATAR_SUPPORT = get('GRAVATAR_SUPPORT', True)
GRAVATAR_DEFAULT = get('GRAVATAR_DEFAULT', 'identicon')

# LOFI Extension
LOFI_SUPPORT = get('LOFI_SUPPORT', True)

# PM Extension
PM_SUPPORT = get('PM_SUPPORT', True)

# AUTHORITY Extension
AUTHORITY_SUPPORT = get('AUTHORITY_SUPPORT', True)
AUTHORITY_STEP_0 = get('AUTHORITY_STEP_0', 0)
AUTHORITY_STEP_1 = get('AUTHORITY_STEP_1', 10)
AUTHORITY_STEP_2 = get('AUTHORITY_STEP_2', 25)
AUTHORITY_STEP_3 = get('AUTHORITY_STEP_3', 50)
AUTHORITY_STEP_4 = get('AUTHORITY_STEP_4', 75)
AUTHORITY_STEP_5 = get('AUTHORITY_STEP_5', 100)
AUTHORITY_STEP_6 = get('AUTHORITY_STEP_6', 150)
AUTHORITY_STEP_7 = get('AUTHORITY_STEP_7', 200)
AUTHORITY_STEP_8 = get('AUTHORITY_STEP_8', 300)
AUTHORITY_STEP_9 = get('AUTHORITY_STEP_9', 500)
AUTHORITY_STEP_10 = get('AUTHORITY_STEP_10', 1000)

# REPUTATION Extension
REPUTATION_SUPPORT = get('REPUTATION_SUPPORT', True)

# ATTACHMENT Extension
ATTACHMENT_SUPPORT = get('ATTACHMENT_SUPPORT', True)
ATTACHMENT_UPLOAD_TO = get('ATTACHMENT_UPLOAD_TO', 'forum/attachments')
ATTACHMENT_SIZE_LIMIT = get('ATTACHMENT_SIZE_LIMIT', 1024 * 1024)

# SMILE Extension
SMILES_SUPPORT = get('SMILES_SUPPORT', True)
EMOTION_SMILE = get('EMOTION_SMILE', '<img src="%sforum/img/smilies/smile.png">' % settings.MEDIA_URL)
EMOTION_NEUTRAL = get('EMOTION_NEUTRAL', '<img src="%sforum/img/smilies/neutral.png">' % settings.MEDIA_URL)
EMOTION_SAD = get('EMOTION_SAD', '<img src="%sforum/img/smilies/sad.png">' % settings.MEDIA_URL)
EMOTION_BIG_SMILE = get('EMOTION_BIG_SMILE', '<img src="%sforum/img/smilies/big_smile.png">' % settings.MEDIA_URL)
EMOTION_YIKES = get('EMOTION_YIKES', '<img src="%sforum/img/smilies/yikes.png">' % settings.MEDIA_URL)
EMOTION_WINK = get('EMOTION_WINK', '<img src="%sforum/img/smilies/wink.png">' % settings.MEDIA_URL)
EMOTION_HMM = get('EMOTION_HMM', '<img src="%sforum/img/smilies/hmm.png">' % settings.MEDIA_URL)
EMOTION_TONGUE = get('EMOTION_TONGUE', '<img src="%sforum/img/smilies/tongue.png">' % settings.MEDIA_URL)
EMOTION_LOL = get('EMOTION_LOL', '<img src="%sforum/img/smilies/lol.png">' % settings.MEDIA_URL)
EMOTION_MAD = get('EMOTION_MAD', '<img src="%sforum/img/smilies/mad.png">' % settings.MEDIA_URL)
EMOTION_ROLL = get('EMOTION_ROLL', '<img src="%sforum/img/smilies/roll.png">' % settings.MEDIA_URL)
EMOTION_COOL = get('EMOTION_COOL', '<img src="%sforum/img/smilies/cool.png">' % settings.MEDIA_URL)
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
SMILES = get('SMILES', SMILES)