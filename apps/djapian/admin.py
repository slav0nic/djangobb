# -*- coding: utf-8 -*-
from django.contrib import admin
from djapian.models import Change


class ChangeAdmin(admin.ModelAdmin):
    """Set what's displayed in admin"""
    list_display = ('content_type', 'object_id', 'action', "date", )
    list_filter = ('content_type', 'action', )


admin.site.register(Change, ChangeAdmin)
