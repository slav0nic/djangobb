# coding: utf-8


from django.conf import settings

from djangobb_forum import settings as djangobb_settings


def forum_settings(request):
    return {
        'forum_settings': djangobb_settings,
        'DEBUG': settings.DEBUG,
    }
