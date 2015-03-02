# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

# Routers provide an easy way of automatically determining the URL conf.
from rest_framework.response import Response
from rest_framework.decorators import list_route


router = routers.DefaultRouter()


class ItemTypeSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=200)
    verbose_name = serializers.CharField(max_length=200)
    short_name = serializers.CharField(max_length=200)

    def to_representation(self, obj):
        return {
            'identifier': obj.get_identifier(),
            'verbose_name': obj.get_verbose_name(),
            'short_name': obj.get_short_name(),
        }


class UrlSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    url = serializers.CharField()


class ItemSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=200)
    verbose_name = serializers.CharField(max_length=200)
    short_name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    urls = UrlSerializer(many=True)

    def to_representation(self, obj):
        return {
            'identifier': obj.get_identifier(),
            'verbose_name': obj.get_verbose_name(),
            'short_name': obj.get_short_name(),
            'description': obj.get_description(),
            'urls': obj.get_urls(),
        }


class ItemTypeViewSet(viewsets.GenericViewSet):
    lookup_field = 'identifier'
    serializer_class = ItemTypeSerializer

    def get_object(self):
        from . import registry
        return registry.registry._registry[self.kwargs['identifier']]

    def get_queryset(self):
        from . import registry
        return registry.registry._registry.values()

    def list(self, request, *args, **kwargs):
        instance = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


router.register(r'item_types', ItemTypeViewSet, base_name='item_type')


class ItemViewSet(viewsets.GenericViewSet):
    serializer_class = ItemSerializer

    @list_route(('GET',))
    def search(self, request, *args, **kwargs):
        from . import registry
        instance = registry.registry.search(q=kwargs.get('q', ''))
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

router.register(r'items', ItemViewSet, base_name='item')


# # Serializers define the API representation.
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'is_staff')
#
#
# # ViewSets define the view behavior.
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# router.register(r'users', UserViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
