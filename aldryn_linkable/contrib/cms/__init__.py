# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import cms.models
from aldryn_linkable.registry import ModelItemType, registry


class CmsPageItemType(ModelItemType):
    model = cms.models.Page
    search_fields = (
        'title_set__title',
    )
    name = 'cms Page'
    identifier = 'cms_page'


registry.register(CmsPageItemType())
