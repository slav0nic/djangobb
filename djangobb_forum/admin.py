# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import User

from djangobb_forum.models import Category, Forum, Topic, Post, Profile, Reputation,\
    Report, Ban


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']

class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count']
    raw_id_fields = ['moderators', 'last_post']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'post_count']
    search_fields = ['name']
    raw_id_fields = ['user', 'subscribers', 'last_post']

class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created', 'updated', 'summary']
    search_fields = ['body']
    raw_id_fields = ['topic', 'user', 'updated_by']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'time_zone', 'location', 'language']
    raw_id_fields = ['user']

class ReputationAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'post', 'sign', 'time', 'reason']
    raw_id_fields = ['from_user', 'to_user', 'post']

class ReportAdmin(admin.ModelAdmin):
    list_display = ['reported_by', 'post', 'zapped', 'zapped_by', 'created', 'reason']
    raw_id_fields = ['reported_by', 'post']

class BanAdmin(admin.ModelAdmin):
    list_display = ['user', 'ban_start', 'ban_end', 'reason']
    raw_id_fields = ['user']

class UserAdmin(auth_admin.UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        return patterns('',
                        url(r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password), name='user_change_password'),
                        ) + super(auth_admin.UserAdmin, self).get_urls()


admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Reputation, ReputationAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Ban, BanAdmin)

admin.site.disable_action('delete_selected')  #disabled, because delete_selected ignoring delete model method