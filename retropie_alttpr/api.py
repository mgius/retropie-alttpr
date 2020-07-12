"""
Interactions with ALTTPR API via pyz3r library

Most interactions with pyz3r are async functions wrapped to look like sync
functions, with some heavy caching and such going on as well.
"""

from retropie_alttpr import cache, util

from loguru import logger
import pyz3r
import pyz3r.http
import pyz3r.alttpr


@cache.misc.transparent_cache('randomizer_settings')
@util.async_to_sync
async def fetch_randomizer_settings():
    """ Load settings from ALTTPR website """
    # load default randomizer settings from alttpr
    logger.debug("Fetching randomizer settings from alttpr", enqueue=True)
    alttpr = await pyz3r.alttpr()
    all_settings = await alttpr.randomizer_settings()

    return all_settings


async def fetch_base_patch(site: pyz3r.http.site, patch_hash):
    return await site.retrieve_binary(f"/bps/{patch_hash}.bps")


@util.async_to_sync
async def generate_seed(settings: dict):
    seed = await pyz3r.alttpr(
        settings=settings
    )

    base_patch_hash = seed.data['current_rom_hash']

    if not cache.base_patch.exists(base_patch_hash):
        base_patch = await fetch_base_patch(seed.site, base_patch_hash)
        cache.base_patch.put(base_patch_hash, base_patch)

    logger.info(f"Generated Hash: {seed.hash}")
    logger.info(f"Generated Code: {seed.code}")

    return seed


@util.async_to_sync
async def validate_rom(rom_filename):
    await pyz3r.rom.read(rom_filename)


@util.async_to_sync
async def generate_rom(settings: dict):
    seed = await pyz3r.alttpr(
        settings=settings
    )

    base_rom = list(cache.misc.get('base_zelda_rom'))

    patched_rom = await seed.create_patched_game(base_rom)

    return bytes(patched_rom)
