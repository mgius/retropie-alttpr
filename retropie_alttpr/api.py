"""
Interactions with ALTTPR API via pyz3r library

Most interactions with pyz3r are async functions wrapped to look like sync
functions, with some heavy caching and such going on as well.
"""

from retropie_alttpr import cache, util

from loguru import logger
import pyz3r


@cache.misc.transparent_cache('randomizer_settings')
@util.async_to_sync
async def fetch_randomizer_settings():
    """ Load settings from ALTTPR website """
    # load default randomizer settings from alttpr
    logger.debug("Fetching randomizer settings from alttpr", enqueue=True)
    alttpr = await pyz3r.alttpr()
    all_settings = await alttpr.randomizer_settings()

    return all_settings


@util.async_to_sync
async def _generate_rom(settings, base_rom_filename, patched_rom_filename):
    logger.debug(f"Generating ROM with settings {settings}", enqueue=True)
    seed = await pyz3r.alttpr(
        settings=settings
    )

    base_rom = await pyz3r.rom.read(base_rom_filename)

    patched_rom = await seed.create_patched_game(base_rom)

    await pyz3r.rom.write(patched_rom, patched_rom_filename)

    logger.info(f"Generated Hash: {seed.hash}")
    logger.info(f"Generated Code: {seed.code}")


def generate_rom(settings: dict) -> bytes:
    base_rom_data = cache.misc.get('base_zelda_rom')
    with util.in_memory_tempfile() as base_rom_file, util.in_memory_tempfile() as patched_rom_file:
        base_rom_file.write(base_rom_data)
        base_rom_file.flush()
        _generate_rom(settings, base_rom_file.name, patched_rom_file.name)

        return base_rom_file.read()


@util.async_to_sync
async def validate_rom(rom_filename):
    await pyz3r.rom.read(rom_filename)
