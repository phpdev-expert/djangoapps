from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class Cacher:
    @staticmethod
    def get(key):
        items = cache.get(key)
        return items

    @staticmethod
    def set(key, items):
        cache.set(key, items, timeout=CACHE_TTL)

    @staticmethod
    def delete(key):
        cache.delete(key)

    @staticmethod
    def delete_pattern(key):
        cache.delete_pattern(key)
