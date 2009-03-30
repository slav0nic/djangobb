# -*- coding: utf-8
from django.contrib import admin
from forum.models import Category, Forum, Topic, Post, Profile, Read, Reputation, Report

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']

class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'post_count']
    search_fields = ['name']

class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created', 'updated', 'summary']
    search_fields = ['body']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'time_zone', 'location', 'language']

class ReadAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'time']
    
class ReputationAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'topic', 'sign', 'time', 'reason']
    
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reported_by', 'post', 'zapped', 'zapped_by', 'created', 'reason']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Read, ReadAdmin)
admin.site.register(Reputation, ReputationAdmin)
admin.site.register(Report, ReportAdmin)

#admin.site.unregister(Category)
#admin.site.unregister(Forum)
#admin.site.unregister(Topic)
#admin.site.unregister(Post)
#admin.site.unregister(Profile)
#admin.site.unregister(Read)
#admin.site.unregister(Reputation)
#admin.site.unregister(Report)