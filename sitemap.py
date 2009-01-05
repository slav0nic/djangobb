from django.contrib.sitemaps import Sitemap

from apps.forum.models import Category, Forum, Topic

class SitemapCategory(Sitemap):
    priority = 0.5
    
    def items(self):
        return Category.objects.all()
    
class SitemapForum(Sitemap):
    priority = 0.5
    
    def items(self):
        return Forum.objects.all()
    
class SitemapTopic(Sitemap):
    priority = 0.5
    
    def items(self):
        return Topic.objects.all()