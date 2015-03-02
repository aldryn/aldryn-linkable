# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import


def call_if_callable(fnc):
    if callable(fnc):
        return fnc()
    else:
        return fnc


class ItemType(object):
    """
    An item type provides the interface to search for items of the registered
    type.
    """
    item_type_id = None

    def search(self, q, user=None, page=1, items_per_page=10):
        """
        search for anything that matches the query `q` (a string)
        :param q: the search string
        :param user: a django user object for permission checks
        :param page: page number for pagination
        :param items_per_page: how many items per page
        :return: list, tuple or generator of objects that implement the `Item` interface
        """
        raise NotImplementedError('please implement search for ItemType')

    def get_name(self):
        """
        A unique identifier for this ItemType. This is used to prevent the
        same item type of being registered multiple times and to provide an
        easier way to unregister types.
        :return:
        """
        if hasattr(self, 'name'):
            return self.name
        raise NotImplementedError('please provide a unique name')

    def get_verbose_name(self):
        """
        a relatively short human readable name of up to about 15 characters
        :return:
        """
        if hasattr(self, 'verbose_name'):
            return self.verbose_name
        raise NotImplementedError('either add a class variable `verbose_name` or override get_verbose_name')

    def get_short_name(self):
        """
        A very short human readable name used for menus and filters
        :return:
        """
        if hasattr(self, 'short_name'):
            return self.short_name
        return self.get_verbose_name()

    def get_thumbnail(self):
        """
        A thumbnail for the ItemType. Should return an url to an image
        (will be displayed at approx 200x200). Or an object that can be
        passed to easy-thumbnails for resizing.
        :return:
        """
        if hasattr(self, 'thumbnail'):
            return self.thumbnail
        return ''

    def get_default_item_thumbnail(self):
        """
        A thumbnail used to display for this item, if it does not provide
        anything for an individual item. Same rules as for get_thumbnail()
        apply.
        :return:
        """
        if hasattr(self, 'default_item_thumbnail'):
            return self.default_item_thumbnail
        return self.get_thumbnail()


class ModelItemType(ItemType):
    model = None
    search_fields = ()
    order_by = None

    def search(self, q, user=None, page=1, items_per_page=10):
        from django.db.models import Q
        query = Q()
        for field in self.search_fields:
            for term in q.split(' '):
                query |= Q(**{'{}__icontains'.format(field): term})
        qs = self.model.objects.filter(query)
        if self.order_by:
            qs = qs.order_by(self.order_by)
        slice_start = (page - 1) * items_per_page
        slice_end = (page * items_per_page) + 1
        qs = qs[slice_start:slice_end]
        return {
            'results': qs,
            'has_more': len(qs) > items_per_page
        }

    def get_model(self):
        if self.model is not None:
            return self.model
        raise NotImplementedError('please set a model')

    def get_identifier(self):
        return self.get_model().__module__ + "." + self.get_model().__class__.__name__

    def get_verbose_name(self):
        return self.get_model()._meta.verbose_name.title()


class Item(object):
    """
    Items returned by the search() method of ItemType should return an iterable
    that follow the same interface as this thing. Conveniently subclass Item
    for your own implementations. If your actual objects implement this exact
    interface you can also just return those.
    """

    def __init__(self, obj):
        self.obj = obj

    def get_identifier(self):
        """
        Name/Title of an individual Item. This will be truncated to about 30
        characters.
        :return:
        """
        if hasattr(self, 'identifer'):
            return self.identifier
        raise NotImplementedError('please provide a identifer attribute or '
                                  'override identifer()')

    def get_verbose_name(self):
        """
        Name/Title of an individual Item. This will be truncated to about 30
        characters.
        :return:
        """
        if hasattr(self, 'verbose_name'):
            return self.verbose_name
        raise NotImplementedError('please provide a verbose_name attribute or '
                                  'override verbose_name()')

    def get_short_name(self):
        """
        A very short human readable name used for menus and filters
        :return:
        """
        if hasattr(self, 'short_name'):
            return self.short_name
        return self.get_verbose_name()

    def get_description(self):
        """
        A short pure textual description. Will be truncated to about 200
        characters in default views, but up to 1000 characters displayed
        when looking at details.
        :return:
        """
        if hasattr(self, 'description'):
            return self.description
        return ''

    def get_thumbnail(self):
        """
        A thumbnail for the Item. Same rules as for ItemType.get_thumbnail()
        apply.
        :return:
        """
        if hasattr(self, 'thumbnail'):
            return self.thumbnail
        return ''

    def get_urls(self):
        """
        return a list of dicts containing link targets
        for this object. These are used for the Link widget. The dict should
        contain a machine readable name, a localised human readable name and
        the link. This example is for a Person object:
        [
            {
                'name': 'public_profile',
                'verbose_name': 'Public Profile',
                'url': '/en/profiles/stefanfoulis/'
            },
            {
                'name': 'timeline',
                'verbose_name': 'Timeline',
                'url': '/en/profiles/stefanfoulis/timeline/'
            },
        ]
        :return:
        """
        if hasattr(self, 'urls'):
            return self.urls
        if hasattr(self.obj, 'get_absolute_url'):
            return call_if_callable(self.obj.get_absolute_url)
        raise NotImplemented('get_urls is not implemented, so url selection is not possible')


class Registry(object):
    _registry = dict()

    def register(self, item_type):
        self._registry[item_type.get_identifier()] = item_type

    def search(self, q, limit=100):
        results = []
        for item_type in self._registry.values():
            for item in item_type.search(q=q, items_per_page=limit):
                results.append(item)
        return results
registry = Registry()
