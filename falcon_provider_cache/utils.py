# -*- coding: utf-8 -*-
"""Cache utility."""
# standard library
import hashlib
from typing import Any, Optional, Union

# third-party
import falcon


class CacheProvider:
    """Base Cache Provider Class.

    Args:
        cache_control: A default cache control object.
        user_key: The falcon req.context attribute that contains the username
            or user_id that will be used if private cache is enabled.
    """

    def __init__(self, cache_control: Optional[dict] = None, user_key: Optional[str] = None):
        """Initialize class properties

        **cache_control**

        methods (list): A list of method where caching should be used.
        private (bool): If the caching should be private (applied per user). Requires user_key
            to be set to a valid value.
        timeout (int): The TTL of the cache.
        use_query (limit): If True the request query parameters will be used to generate the
            caches unique key.

        .. code:: python

            class ApiResource(object):
                cache_control = {
                    'enabled': True,
                    'methods': ['GET'],
                    'private': False,
                    'timeout': 10,
                    'use_query': True,
                }
                def on_get(self, req, resp):
                    ...


                cache_control = {
                    'GET': {
                        'enabled': True,
                        'private': False,
                        'timeout': 10,
                        'use_query': True,
                    }
                }
        """
        # TODO: ^^^^^^^^^^^^ change format ??????????????
        self._global_cache_control = {
            'enabled': False,
            'methods': ['GET'],
            'private': False,
            # 'return_errors': True,
            'timeout': 60,
            'use_query': False,
        }
        if cache_control is not None:
            # update global cache control with user provided settings
            self._global_cache_control.update(cache_control)
        self._cache_control = dict(self._global_cache_control)
        self.user_key = user_key  # the req.context attribute to make cache unique per user

    def cache_control(self, cache_control: Optional[dict] = None) -> dict:
        """Return cache control settings.

        Args:
            cache_control: The cache control settings.

        Returns:
            dict: Updated cache control settings.
        """
        cache_control = cache_control or {}
        self._cache_control = dict(self._global_cache_control)
        self._cache_control.update(cache_control)
        return self._cache_control

    def cache_key(
        self, req: falcon.Request, resource: object  # pylint: disable=unused-argument
    ) -> str:
        """Provide a unique redis cache key.

        Starting with falcon 2.0 the path will always have the trailing '/' stripped.

        Args:
            req: The falcon request instance.
            resource: The resource object (provider).

        Returns:
            str: The cache key.
        """
        key = req.path  # using path instead of uri so params is optional
        if self.use_query:
            for k, v in sorted(req.params.items()):
                # build query params
                if isinstance(v, list):  # pragma: no cover
                    # from falcon docs:
                    # where the parameter appears multiple times in the query string, the value
                    # mapped to that parameter key will be a list of all the values in the order
                    # seen.
                    # during testing this did not seem to be the case, possibly and issue
                    # with the falcon TestClient.
                    v = ''.join(sorted(v))
                key += f'{k}{v}'

        if self.private and self.user_key is not None and hasattr(req.context, self.user_key):
            # use token data to make key unique per user
            user_key = str(getattr(req.context, self.user_key))
            if user_key:
                key += user_key
        return hashlib.sha1(key.encode()).hexdigest()  # nosec

    @property
    def enabled(self) -> bool:
        """Return cache control enabled value."""
        return self._cache_control.get('enabled', False)

    @property
    def methods(self) -> list:
        """Return cache control methods value."""
        return self._cache_control.get('methods', ['GET'])

    @property
    def private(self) -> bool:
        """Return cache control private value."""
        return self._cache_control.get('private', False)

    @property
    def timeout(self) -> int:
        """Return cache control timeout value."""
        return self._cache_control.get('timeout', 60)

    @property
    def use_query(self) -> bool:
        """Return cache control use_query value."""
        return self._cache_control.get('use_query', False)


class MemcacheProvider(CacheProvider):
    """Memcache Provider Class.

    Args:
        cache_control: A dict containing the default cache control settings.
        user_key: The falcon req.context attribute that contains the username or
            userid that will be used if private cache is enabled.
        server: The server settings for memcache, can either be a (host, port) tuple for
            a TCP connection or a string containing the path to a UNIX domain socket.
        max_pool_size (int, kwargs): The maximum pool size for Pool Client.
        connect_timeout (int, kwargs): Used to set socket timeout values. By default, timeouts
            are disabled.
        deserializer (callable, kwargs): The deserialization function takes three
            parameters, a key, value and flags and returns the deserialized value.
        no_delay (bool, kwargs): Sets TCP_NODELAY socket option.
        serializer (callable, kwargs): The serialization function takes two arguments,
            a key and a value, and returns a tuple of two elements, the serialized value, and an
            integer in the range 0-65535 (the “flags”).
        timeout (int, kwargs): Used to set socket timeout values. By default, timeouts are
            disabled.
    """

    def __init__(
        self,
        cache_control: Optional[dict] = None,
        user_key: Optional[str] = None,
        server: Optional[Union[str, tuple]] = None,
        **kwargs,
    ):
        """Initialize class properties."""

        super(MemcacheProvider, self).__init__(cache_control, user_key)

        try:
            # third-party
            from falcon_provider_memcache.utils import (  # pylint: disable=import-outside-toplevel
                MemcacheClient,
            )
        except ImportError:  # pragma: no cover
            print(
                'MemcacheProvider requires falcon-provider-memcache to be installed '
                'try "pip install falcon-provider-cache[memcache]".'
            )
            raise

        self.memcache_client = MemcacheClient(server, **kwargs).client

    def get_cache(self, key: str) -> Any:
        """Return cache from memcache

        Args:
            key: The cache key.

        Returns:
            Any: The cached data.
        """
        return self.memcache_client.get(key)

    def set_cache(self, key: str, value: str, timeout: Optional[int] = None):
        """Write cache to Redis

        Args:
            key: The cache key.
            value: The cache value.
            timeout: The cache timeout value.
        """
        timeout = timeout or self.timeout
        self.memcache_client.set(key=key, value=value, expire=timeout)


class RedisCacheProvider(CacheProvider):
    """Redis Cache Provider Class.

    Args:
        cache_control: A dict containing the default cache control settings.
        user_key: The falcon req.context attribute that contains the username or
            userid that will be used if private cache is enabled.
        host: The REDIS host.
        port: The REDIS port.
        db: The REDIS db.
        blocking_pool: Use BlockingConnectionPool instead of ConnectionPool.
        errors (str, kwargs): The REDIS errors policy (e.g. strict).
        max_connections (int, kwargs): The maximum number of connections to REDIS.
        password (str, kwargs): The REDIS password.
        socket_timeout (int, kwargs): The REDIS socket timeout.
        timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.
    """

    def __init__(
        self,
        cache_control: Optional[dict] = None,
        user_key: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        blocking_pool: Optional[bool] = False,
        **kwargs,
    ):
        """Initialize class properties."""
        super(RedisCacheProvider, self).__init__(cache_control, user_key)

        try:
            # third-party
            from falcon_provider_redis.utils import (  # pylint: disable=import-outside-toplevel
                RedisClient,
            )
        except ImportError:  # pragma: no cover
            print(
                'RedisCacheProvider requires falcon-provider-redis to be installed '
                'try "pip install falcon-provider-cache[redis]".'
            )
            raise

        self.redis_client = RedisClient(host, port, db, blocking_pool, **kwargs).client

    def get_cache(self, key: str) -> Any:
        """Return cache from Redis

        Args:
            key: The cache key.

        Returns:
            Any: The cached data.
        """
        return self.redis_client.get(key)

    def set_cache(self, key: str, value: str, timeout: Optional[int] = None):
        """Write cache to Redis

        Args:
            key: The cache key.
            value: The cache value.
            timeout: The cache timeout value in seconds.
        """
        timeout = timeout or self.timeout
        self.redis_client.setex(name=key, time=timeout, value=value)
