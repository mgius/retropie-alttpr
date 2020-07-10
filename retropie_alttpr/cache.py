"""
It might be better to use something like a memcached/redis frontend
instead of rolling my own thing.
"""

from typing import Optional

from pathlib import Path
from dataclasses import dataclass, InitVar

import json
from functools import wraps


DEFAULT_BASE_DIR = Path("~/.cache/retropie_alttpr")


def _ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True)


def json_encode_to_bytes(obj):
    return json.dumps(obj).encode('utf-8')


@dataclass
class CachedFile:
    subdir: Path
    base_dir: Path = DEFAULT_BASE_DIR
    cache_dir: InitVar[Path] = None

    def __post_init__(self, cache_dir):
        if cache_dir is None:
            self.cache_dir = self.base_dir.expanduser().joinpath(self.subdir)

        _ensure_dir(self.cache_dir)

    def get(self, hashval: str) -> Optional[bytes]:
        path = self.cache_dir.joinpath(hashval)
        if not path.exists():
            return None
        return path.read_bytes()

    def exists(self, hashval: str) -> bool:
        path = self.cache_dir.joinpath(hashval)
        return path.exists()

    def put(self, hashval: str, value: bytes):
        path = self.cache_dir.joinpath(hashval)
        path.touch()
        path.write_bytes(value)

    def transparent_cache(self, hashval: str, decode=json.loads, encode=json_encode_to_bytes):
        """ Transparently cache the results of the wrapped function to a file """
        def deco_fun(fun):
            @wraps(fun)
            def wrapped_fun(*args, **kwargs):
                if not self.exists(hashval):
                    val = fun(*args, **kwargs)
                    self.put(hashval, encode(val))
                else:
                    val = decode(self.get(hashval))

                return val

            return wrapped_fun

        return deco_fun


base_patch = CachedFile(Path("base_patches"))

seed = CachedFile(Path("seeds"))

misc = CachedFile(Path("misc"))

config = CachedFile(Path("configs"))
