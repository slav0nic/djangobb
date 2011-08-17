from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils import translation
from django.conf import settings as global_settings

from djangobb_forum import settings as forum_settings

class LastLoginMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
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

class UsersOnline(object):
    def process_request(self, request):
        now = datetime.now()
        delta = now - timedelta(minutes=forum_settings.USER_ONLINE_TIMEOUT)
        users_online = cache.get('users_online', {})
        guests_online = cache.get('guests_online', {})

        if request.user.is_authenticated():
            users_online[request.user.id] = now
        else:
            guest_sid = request.COOKIES.get(global_settings.SESSION_COOKIE_NAME, '')
            guests_online[guest_sid] = now

        for user_id in users_online.keys():
            if users_online[user_id] < delta:
                del users_online[user_id]

        for guest_id in guests_online.keys():
            if guests_online[guest_id] < delta:
                del guests_online[guest_id]

        cache.set('users_online', users_online, 60*60*24)
        cache.set('guests_online', guests_online, 60*60*24)
