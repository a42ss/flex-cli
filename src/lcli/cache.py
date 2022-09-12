import datetime
import errno
import hashlib
import os
import shelve

from lcli.exceptions import LcliException


class CacheNotFoundException(LcliException):
    pass


class Cache(object):
    lifetime: int
    cache_key: str

    class Constants:
        EXPIRE_ON = "expire_on"
        LIFETIME = "lifetime"
        DATA = "data"

    def __init__(self, cache_directory: str, cache_keys: list, lifetime: int = 0):
        """

        :type cache_keys: list
        :type cache_directory: str
        """
        self.lifetime = lifetime
        self.cache_key = self.generate_cache_key(cache_keys)
        try:
            os.makedirs(cache_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.cache_path = os.path.join(cache_directory, self.cache_key)

    def save(self, data):
        cache = shelve.open(self.cache_path)
        cache[self.cache_key] = {
            self.Constants.DATA: data,
            self.Constants.LIFETIME: self.lifetime,
            self.Constants.EXPIRE_ON: datetime.datetime.now()
            + datetime.timedelta(self.lifetime),
        }
        cache.close()

    @classmethod
    def generate_cache_key(cls, cache_keys: list) -> str:
        md5 = hashlib.md5(usedforsecurity=False)

        if len(cache_keys) == 1:
            md5.update(cache_keys[0].encode("utf-8"))
        else:
            md5.update("".join(cache_keys).encode("utf-8"))
        return md5.hexdigest()

    def get(self):
        result = None
        cache = shelve.open(self.cache_path)
        if self.cache_key in cache:
            cache_data = cache[self.cache_key]

            if (
                cache_data[self.Constants.LIFETIME] == 0
                or cache_data[self.Constants.EXPIRE_ON] > datetime.datetime.now()
            ):
                result = cache_data[self.Constants.DATA]
            else:
                del cache[self.cache_key]

        cache.close()

        if result is not None:
            return result

        raise CacheNotFoundException("Cache not found")
