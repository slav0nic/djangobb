from django.core.cache import cache

from apps.forum import settings as forum_settings

class LastLoginMiddleware(object):
    def process_request(self, request):
        cache.set(str(request.user.id), True, forum_settings.USER_ONLINE_TIMEOUT)