from pathlib import Path
import tempfile
import unittest

from retropie_alttpr import cache


class TestCachedFile(unittest.TestCase):
    def setUp(self):
        self.test_cache_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.test_cache_dir.name)

    def _create_cacher(self, name='test'):
        return cache.CachedFile(Path(name), base_dir=self.base_dir)

    def test_cacher(self):
        hashval = 'asdf'
        contents = b'123456'
        cacher = self._create_cacher()
        cacher.put(hashval, contents)
        fetched = cacher.get(hashval)

        self.assertEqual(contents, fetched)

    def test_read_missing_value(self):
        hashval = 'asdf'
        cacher = self._create_cacher()
        self.assertIsNone(cacher.get(hashval))

    def test_independence(self):
        hashval = 'asdfc'
        contents = b'1234'
        cacherA = self._create_cacher('cacherA')
        cacherB = self._create_cacher('cacherB')

        cacherA.put(hashval, contents)
        self.assertIsNone(cacherB.get(hashval))
