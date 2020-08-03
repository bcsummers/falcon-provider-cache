# -*- coding: utf-8 -*-
"""Testing conf module."""
# third-party
import pytest
from falcon import testing

from .Memcache.app import app_memcache_enabled, app_memcache_global
from .Redis.app import app_redis


@pytest.fixture
def client_memcache_enabled() -> testing.TestClient:
    """Create testing client fixture for hook app"""
    return testing.TestClient(app_memcache_enabled)


@pytest.fixture
def client_memcache_global() -> testing.TestClient:
    """Create testing client fixture for hook app"""
    return testing.TestClient(app_memcache_global)


@pytest.fixture
def client_redis() -> testing.TestClient:
    """Create testing client fixture for middleware app"""
    return testing.TestClient(app_redis)
