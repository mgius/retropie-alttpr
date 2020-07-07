"""
It might be better to use something like a memcached/redis frontend
instead of rolling my own thing.
"""

from typing import Optional

from pathlib import Path
from dataclasses import dataclass, InitVar


DEFAULT_BASE_DIR = Path("~/.cache/retropie_alttpr")


def _ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True)


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


base_patch = CachedFile(Path("base_patches"))

seed = CachedFile(Path("seeds"))

misc = CachedFile(Path("misc"))
