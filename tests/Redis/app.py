# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# standard library
import os

# third-party
import falcon

# first-party
from falcon_provider_cache.middleware import CacheMiddleware
from falcon_provider_cache.utils import RedisCacheProvider

# redis server
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
redis_provider = RedisCacheProvider(host=REDIS_HOST, port=REDIS_PORT, user_key='user_key')


class RedisResource:
    """Redis cache middleware testing resource."""

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
        key = req.get_param('key')
        resp.body = 'test'
        resp.body = f'{key}-worked'  # pylint: disable=no-member
        resp.status_code = falcon.HTTP_OK


app_redis = falcon.API(middleware=[CacheMiddleware(redis_provider)])
app_redis.add_route('/middleware', RedisResource())
