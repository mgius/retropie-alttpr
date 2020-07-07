import asyncio
import functools
import json
import pyz3r

from retropie_alttpr import cache

from loguru import logger


def async_to_sync(fun):
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        return asyncio.run(fun(*args, **kwargs))

    return wrapped


@async_to_sync
async def _fetch_randomizer_settings():
    """ Load presets from ALTTPR website """
    # load default randomizer settings from alttpr
    logger.debug("Fetching presets from alttpr", enqueue=True)
    alttpr = await pyz3r.alttpr()
    all_settings = await alttpr.randomizer_settings()

    return all_settings


def fetch_randomizer_settings():
    cache_key = 'randomizer_settings'
    all_settings = cache.misc.get(cache_key)
    if all_settings is None:
        all_settings = _fetch_randomizer_settings()
        cache.misc.put('cache_key', json.dumps(all_settings).encode('utf-8'))
    else:
        all_settings = json.loads(all_settings)

    return all_settings
