# -*- coding: utf-8
from django.contrib import admin

from forum.models import Category, Forum, Topic, Post, Profile, Read,\
    Reputation, Report, Ban


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']

class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'post_count']
    search_fields = ['name']
    raw_id_fields = ['user', 'subscribers', 'last_post']

class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created', 'updated', 'summary']
    search_fields = ['body']
    raw_id_fields = ['topic', 'user']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'time_zone', 'location', 'language']

class ReadAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'time']
    
class ReputationAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'topic', 'sign', 'time', 'reason']
    raw_id_fields = ['from_user', 'to_user', 'topic']

class ReportAdmin(admin.ModelAdmin):
    list_display = ['reported_by', 'post', 'zapped', 'zapped_by', 'created', 'reason']
    raw_id_fields = ['reported_by', 'post']

class BanAdmin(admin.ModelAdmin):
    list_display = ['user', 'ban_start', 'ban_end', 'reason']
    raw_id_fields = ['user']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Read, ReadAdmin)
admin.site.register(Reputation, ReputationAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Ban, BanAdmin)