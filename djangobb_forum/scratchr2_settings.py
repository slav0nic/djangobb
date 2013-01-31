#DjangoBB Forum Settings
# Described here: https://bitbucket.org/slav0nic/djangobb/src/a4c0272533a9/djangobb_forum/settings.py
DJANGOBB_FORUM_BASE_TITLE = 'Scratch Forums'
DJANGOBB_PM_SUPPORT = False
DJANGOBB_HEADER = 'Scratch Forums'
DJANGOBB_TAGLINE = ''
DJANGOBB_LOFI_SUPPORT = False
DJANGOBB_REPUTATION_SUPPORT = False
DJANGOBB_ATTACHMENT_SUPPORT = False
DJANGOBB_GRAVATAR_SUPPORT = False
DJANGOBB_DISPLAY_PROFILE_MENU_OPTIONS = False
DJANGOBB_DISPLAY_AVATAR_OPTIONS = False
DJANGOBB_DISPLAY_USERTITLE = False
# The value is the topic id where deleted posts should be sent
DJANGOBB_SOFT_DELETE_POSTS = 412
# The value is the forum id where deleted topics should be sent
DJANGOBB_SOFT_DELETE_TOPICS = 2
DJANGOBB_ALLOW_POLLS = False
DJANGOBB_POST_FLOOD = True
DJANGOBB_POST_FLOOD_SLOW = 120
DJANGOBB_POST_FLOOD_MED = 60
DJANGOBB_TOPIC_CLOSE_DELAY = 24 * 60 * 60

DJANGOBB_TOPIC_PAGE_SIZE = 20
DJANGOBB_FORUM_PAGE_SIZE = 25
DJANGOBB_SIGNATURE_MAX_LINES = 10
DJANGOBB_SIGNATURE_MAX_LENGTH = 2000
DJANGOBB_AUTHORITY_SUPPORT = False
DJANGOBB_DEFAULT_TIME_ZONE = 0
DJANGOBB_IMAGE_HOST_WHITELIST = r'(?:(?:tinypic|photobucket)\.com|imageshack\.us|modshare\.tk|(?:scratchr|wikipedia|wikimedia|modshare)\.org|\.edu)$'
DJANGOBB_LANGUAGE_FILTER = r'(?i)\b(fugly|(\w*?)fuck(\w*?)|f(u|v|\*)?c?k(ing?)?|(\w*?)sh(i|1|l)t(\w*?)|cr(a|@|\*)p(per|ped|y)?|(bad|dumb|jack)?(a|@)ss(h(o|0)le|wipe)?|(bad|dumb|jack)?(a|@)rse(h(o|0)le|wipe)?|bastard|b(i|1|l|\*)?t?ch(e?s)?|cunt|cum|(god?)?dam(n|m)(it)?|douche(\w*?)|(new)?fag(got|gat)?|frig(gen|gin|ging)?|omfg|piss(\w*?)|porn|rape|retard|sex|s e x|shat|slut|tit|wh(o|0)re(\w*?)|wt(f|fh|h))(s|ed)?\b'
