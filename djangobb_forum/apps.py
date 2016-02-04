from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ForumConfig(AppConfig):
    name = 'djangobb_forum'
    verbose_name = _('DjangoBB Forum')

    def ready(self):
        from . import signals  # NOQA
