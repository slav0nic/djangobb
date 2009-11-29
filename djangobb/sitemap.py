from django.contrib.sitemaps import Sitemap
from forum.models import Forum, Topic


class SitemapForum(Sitemap):
    priority = 0.5

    def items(self):
        return Forum.objects.all()


class SitemapTopic(Sitemap):
    priority = 0.5

    def items(self):
        return Topic.objects.all()