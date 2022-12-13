"""Test middleware memcache provider module."""
# standard library
import time

# third-party
from falcon.testing import Result


def test_middleware_get(client_memcache_global: object) -> None:
    """Testing GET method

    Args:
        client_memcache_global (fixture): The test client.
    """
    params = {'key': ['middleware', 'null']}
    response: Result = client_memcache_global.simulate_get('/middleware', params=params)

    # make request to cache
    if response.headers.get('x-cache') == 'MISS':
        response = client_memcache_global.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'HIT'


def test_middleware_get_cache_timeout(client_memcache_global: object) -> None:
    """Testing GET method

    Args:
        client_memcache_global (fixture): The test client.
    """
    # make request to ensure data is cached
    params = {'key': ['middleware', 'null']}
    response: Result = client_memcache_global.simulate_get('/middleware', params=params)

    # assume cache timeout is set to 2 seconds
    time.sleep(3)
    response = client_memcache_global.simulate_get('/middleware', params=params)

    assert response.text == 'middleware-worked'
    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'MISS'
