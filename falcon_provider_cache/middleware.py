# -*- coding: utf-8 -*-
"""Falcon cache provider middleware module."""
# third-party
import falcon


class CacheMiddleware:
    """Cache middleware module.

    Args:
        provider (CacheProvider): An instance of cache provider (memcache or Redis).
    """

    def __init__(self, provider: object):
        """Initialize class properties."""
        self.provider = provider

    def _testing(self, req):
        """Update req context with values for testing."""
        if hasattr(self, 'user_key'):
            # inject a test user_key for pytest monkeypatch
            req.context.user_key = self.user_key  # pylint: disable=no-member

    def process_resource(
        self, req: falcon.Request, resp: falcon.Response, resource: object, params: dict
    ):  # pylint: disable=unused-argument
        """Process the request after routing and provide caching service."""
        # for pytest testing
        self._testing(req)

        # update the cache control for the current resource
        cache_control = {}
        if hasattr(resource, 'cache_control') and isinstance(resource.cache_control, dict):
            cache_control = resource.cache_control

        # update cache control
        self.provider.cache_control(cache_control)

        if self.provider.enabled:
            cache_key = self.provider.cache_key(req, resource)
            try:
                cache_data = self.provider.get_cache(cache_key)
            except Exception as e:  # pragma: no cover; pylint: disable=broad-except
                # cache is best effort, process normally if cache not available
                cache_data = None
                if hasattr(resource, 'log'):
                    resource.log.error(f'[cache-provider] Failled reading from cache ({e}).')

            if cache_data is not None:
                resp.context.setdefault('cache_data', cache_data)
                resp.context['response_cached'] = True
                resp.complete = True  # signal short-circuit for response processing

    def process_response(
        self, req: falcon.Request, resp: falcon.Response, resource: object, req_succeeded: bool
    ):
        """Set or delete cache for provided resources."""
        if not self.provider.enabled:
            return

        if req_succeeded and self.provider.enabled:
            resp.set_header('X-Cache', 'MISS')  # set x-cache header to default of no cache
            cache_key: str = self.provider.cache_key(req, resource)

            if req.method in self.provider.methods:
                if resp.context.get('cache_data') is not None:
                    # set body to cached data and stop response
                    resp.set_header('X-Cache', 'HIT')  # update x-cache header for HIT (from cache)
                    resp.body = resp.context.get('cache_data')
                elif resp.body is not None:
                    # cache data
                    try:
                        self.provider.set_cache(cache_key, resp.body)
                    except Exception as e:  # pragma: no cover; pylint: disable=broad-except
                        # cache is best effort, process normally if cache not available
                        if hasattr(resource, 'log'):
                            resource.log.error(f'[cache-provider] Failled writing to cache ({e}).')
