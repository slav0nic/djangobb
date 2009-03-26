from django.conf import settings

ACCOUNT_DOMAIN = getattr(settings, 'ACCOUNT_DOMAIN', 'fix.your.settings.com')
ACCOUNT_AUTH_KEY_TIMEOUT = getattr(settings, 'ACCOUNT_AUTH_KEY_TIMEOUT', 60 * 60 * 24)
