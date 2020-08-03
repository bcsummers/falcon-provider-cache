=====================
falcon-provider-cache
=====================

|build| |coverage| |code-style| |pre-commit|

A falcon middleware cache provider using Memcache or Redis.

------------
Installation
------------

Install the extension via pip. For memcache provider use ``[memcache]`` and for redis provider use ``[redis]``.

.. code:: bash

    > pip install falcon-provider-cache[memcache]
    > pip install falcon-provider-cache[redis]

--------
Overview
--------

This package provides a middleware cache component for the Falcon framework. This component uses either the **falcon-provider-memcache** or **falcon-provider-redis** package depending on install options. These memcache and redis provider modules use singletons to enable sharing the backend connections.

.. IMPORTANT:: Caching is best effort. If the caching connection on the backend is not available the request will still process. A log entry will be written if a ``log`` property is available in ``resource``.

For caching enabled API endpoints the middleware will add the **X-Cache** header with a value of **MISS** if a non-cached response is returned and **HIT** if a cached response is returned. For non-caching endpoint no header will be added.

.. NOTE:: When instantiating the cache profile a **user_key** can be provided. The **user_key** is a ``resource`` property (typically provided by an auth provider) that defines a unique id for the user.

--------
Requires
--------
* Falcon - https://pypi.org/project/falcon/

Extra Requires
--------------
* falcon-provider-memcache - https://github.com/bcsummers/falcon-provider-memcache
* falcon-provider-redis - https://github.com/bcsummers/falcon-provider-redis

-------------
Cache Control
-------------

The cache_control dictionary defines the caching behavior. The cache control configuration can be globally defined when creating the cache provider or in each API resource. Global settings will be overwritten by resource settings.

+-----------+-----------+--------------------------------------------------------------------------+
| Control   | Default   | Description                                                              |
+===========+===========+==========================================================================+
| enabled   | False     | Set to True to enable caching.                                           |
+-----------+-----------+--------------------------------------------------------------------------+
| methods   | ['GET']   | The HTTP methods to enable for caching.                                  |
+-----------+-----------+--------------------------------------------------------------------------+
| private   | False     | Make the cache private to the current user (requires user_key to be      |
|           |           | provided).                                                               |
+-----------+-----------+--------------------------------------------------------------------------+
| timeout   | 60        | Set the cache timeout (seconds).                                         |
+-----------+-----------+--------------------------------------------------------------------------+
| use_query | False     | Enable the use of query params to define cache unique key.               |
+-----------+-----------+--------------------------------------------------------------------------+

.. code:: python

    cache_control = {
        'enabled': True,
        'methods': ['GET'],
        'private': False,
        'timeout': 15,
        'use_query': True,
    }

--------
Memcache
--------

.. code:: python

    import os
    import falcon
    from falcon_provider_cache.middleware import CacheMiddleware
    from falcon_provider_cache.utils import MemcacheProvider

    # Memcached
    MEMCACHE_HOST = os.getenv('MEMCACHE_HOST', 'localhost')
    MEMCACHE_PORT = int(os.getenv('MEMCACHE_PORT', '11211'))


    class MemcacheCachingResource(object):
        """Memcache middleware caching resource."""

        cache_control = {
            'enabled': True,
            'methods': ['GET'],
            'private': False,
            'timeout': 2,
            'use_query': True,
        }

        def on_get(self, req, resp):
            """Support GET method."""
            key = req.get_param('key')
            resp.body = f'{key}-worked'
            resp.status_code = falcon.HTTP_OK

    cache_provider = MemcacheProvider(server=(MEMCACHE_HOST, MEMCACHE_PORT))
    app = falcon.API(middleware=[CacheMiddleware(cache_provider)])
    app.add_route('/middleware', MemcacheCachingResource())

-----
Redis
-----

.. code:: python

    import os

    import falcon
    import redis

    from falcon_provider_cache.middleware import CacheMiddleware
    from falcon_provider_cache.utils import RedisCacheProvider

    # redis server
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))


    class RedisCacheResource(object):
        """Redis cache middleware testing resource."""

        cache_control = {
            'enabled': True,
            'methods': ['GET'],
            'private': False,
            'timeout': 2,
            'use_query': True,
        }

        def on_get(self, req, resp):
            """Support GET method."""
            key = req.get_param('key')
            resp.body = f'{key}-worked'
            resp.status_code = falcon.HTTP_OK

    cache_provider = RedisCacheProvider(host=REDIS_HOST, port=REDIS_PORT, user_key='user_key')
    app = falcon.API(middleware=[CacheMiddleware(cache_provider)])
    app.add_route('/middleware', RedisCacheResource())

-----------
Development
-----------

Installation
------------

After cloning the repository, all development requirements can be installed via pip. For linting and code consistency the pre-commit hooks should be installed.

.. code:: bash

    > pip install falcon-provider-cache[dev]
    > pre-commit install

Testing
-------

Testing requires that Memcache and Redis be installed and running.

For Redis the default host is localhost and the default port is 6379. These values can be overwritten by using the REDIS_HOST and REDIS_PORT environment variables.

For Memcache the default host is localhost and the default port is 11211. These values can be overwritten by using the MEMCACHE_HOST and MEMCACHE_PORT environment variables.

.. code:: bash

    > pytest --cov=falcon_provider_cache --cov-report=term-missing tests/

.. |build| image:: https://github.com/bcsummers/falcon-provider-cache/workflows/build/badge.svg
    :target: https://github.com/bcsummers/falcon-provider-cache/actions

.. |coverage| image:: https://codecov.io/gh/bcsummers/falcon-provider-cache/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/bcsummers/falcon-provider-cache

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
