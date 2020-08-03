# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# standard library
import os

# third-party
import falcon

# first-party
from falcon_provider_cache.middleware import CacheMiddleware
from falcon_provider_cache.utils import MemcacheProvider

# Memcached
MEMCACHE_HOST = os.getenv('MEMCACHE_HOST', 'localhost')
MEMCACHE_PORT = int(os.getenv('MEMCACHE_PORT', '11211'))
memcache_provider = MemcacheProvider(server=(MEMCACHE_HOST, MEMCACHE_PORT))


class MemcacheEnableResource:
    """Memcache middleware testing resource."""

    cache_control = {
        'enabled': True,
        'methods': ['GET'],
        'private': False,
        'timeout': 2,
        'use_query': True,
    }

    def on_get(
        self, req: falcon.Request, resp: falcon.Response,
    ):  # pylint: disable=no-self-use
        """Support GET method."""
        key: str = req.get_param('key')
        resp.body = f'{key}-worked'
        resp.status_code = falcon.HTTP_OK


app_memcache_enabled = falcon.API(middleware=[CacheMiddleware(memcache_provider)])
app_memcache_enabled.add_route('/middleware', MemcacheEnableResource())


class MemcacheGlobalResource:
    """Memcache middleware testing resource."""

    cache_control = {
        'enabled': True,
        'methods': ['GET'],
        'private': True,
        'timeout': 2,
        'use_query': True,
    }

    def on_get(
        self, req: falcon.Request, resp: falcon.Response,
    ):  # pylint: disable=no-self-use
        """Support GET method."""
        key: str = req.get_param('key').split(',')[0]
        resp.body = f'{key}-worked'
        resp.status_code = falcon.HTTP_OK


cache_control = {
    'enabled': True,
    'methods': ['GET'],
    'private': False,
    'timeout': 30,
    'use_query': False,
}
error_data = {
    'code': 1234,
    'description': 'An unexpected caching error occurred.',
    'title': 'Internal Server Error',
}
# provider with global cache_control
memcache_provider_global_cache_control = MemcacheProvider(
    cache_control=cache_control,
    error_data=error_data,
    user_key='user_id',
    server=(MEMCACHE_HOST, MEMCACHE_PORT),
)
app_memcache_global = falcon.API(
    middleware=[CacheMiddleware(memcache_provider_global_cache_control)]
)
app_memcache_global.add_route('/middleware', MemcacheGlobalResource())
