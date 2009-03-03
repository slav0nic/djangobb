from django.core.cache import cache
from django.utils import translation

from apps.forum import settings as forum_settings

class LastLoginMiddleware(object):
    def process_request(self, request):
        cache.set(str(request.user.id), True, forum_settings.USER_ONLINE_TIMEOUT)

class ForumMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            profile = request.user.forum_profile
            language = translation.get_language_from_request(request)

            if not profile.language:
                profile.language = language
                profile.save()

            if profile.language and profile.language != language:
                request.session['django_language'] = profile.language
                translation.activate(profile.language)
                request.LANGUAGE_CODE = translation.get_language()
