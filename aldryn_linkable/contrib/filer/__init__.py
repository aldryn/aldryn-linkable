# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import filer.models
from aldryn_linkable.registry import ModelItemType, registry


class FilerFileItemType(ModelItemType):
    model = filer.models.File
    search_fields = (
        'name',
        'description',
        'original_filename',
        'sha1',
    )
    name = 'Filer File'
    identifier = 'filer_file'


registry.register(FilerFileItemType())
