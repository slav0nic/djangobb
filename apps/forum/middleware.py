#from datetime import datetime
#from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.conf import settings
#from django.core.urlresolvers import reverse

class LastLoginMiddleware(object):
    def process_request(self, request):
        cache.set(str(request.user.id), True, settings.FORUM_USER_ONLINE_TIMEOUT)