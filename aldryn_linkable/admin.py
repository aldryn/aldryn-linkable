# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from aldryn_linkable.models import Api
from django.contrib import admin


class LinkableAdmin(admin.ModelAdmin):
    """
    dummy admin to get our urls in there
    """
    def get_urls(self):
        from .urls import urlpatterns
        return urlpatterns

admin.site.register(Api, LinkableAdmin)
