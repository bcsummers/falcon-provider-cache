# -*- coding: utf-8 -*-
"""Test middleware redis provider module."""
# standard library
import time

# third-party
from falcon.testing import Result

# first-party
from falcon_provider_cache.middleware import CacheMiddleware

# required for monkeypatch
from .app import RedisResource


def test_redis_get_authenticated(client_redis: object, monkeypatch: object) -> None:
    """Testing GET method

    Args:
        client_redis(fixture): The test client.
        monkeypatch (object): Pytest _pytest.monkeypatch.MonkeyPatch object.
    """
    monkeypatch.setattr(CacheMiddleware, 'user_key', 123, raising=False)
    RedisResource.cache_control['enabled'] = True
    RedisResource.cache_control['private'] = True

    params = {'key': 'middleware', 'coverage': ['one', 'two']}
    response: Result = client_redis.simulate_get('/middleware', params=params)

    # make request to cache
    if response.headers.get('x-cache') == 'MISS':
        response = client_redis.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'HIT'


def test_redis_get_unauthenticated(client_redis: object) -> None:
    """Testing GET method

    Args:
        client_redis(fixture): The test client.
    """
    RedisResource.cache_control['enabled'] = True

    params = {'key': 'middleware', 'coverage': ['one', 'two']}
    response: Result = client_redis.simulate_get('/middleware', params=params)

    # make request to cache
    if response.headers.get('x-cache') == 'MISS':
        response = client_redis.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'HIT'


def test_redis_get_cache_timeout(client_redis: object) -> None:
    """Testing GET method

    Args:
        client_redis(fixture): The test client.
    """
    RedisResource.cache_control['enabled'] = True

    # make request to ensure data is cached
    params = {'key': 'middleware'}
    response: Result = client_redis.simulate_get('/middleware', params=params)

    # assume cache timeout is set to 2 seconds
    time.sleep(3)
    response = client_redis.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'MISS'


def test_redis_get_disable(client_redis):
    """Testing GET method

    Args:
        client_redis(fixture): The test client.
    """
    RedisResource.cache_control['enabled'] = False

    params = {'key': 'middleware'}
    response: Result = client_redis.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') is None
