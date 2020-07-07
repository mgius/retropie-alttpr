import asyncio
import pyz3r

import click

from loguru import logger

from retropie_alttpr import util



async def generate_rom(settings, base_rom_filename, patched_rom_filename):
    logger.debug(f"Generating ROM with settings {settings}")
    seed = await pyz3r.alttpr(
        settings=settings
    )

    base_rom = await pyz3r.rom.read(base_rom_filename)

    patched_rom = await seed.create_patched_game(base_rom)

    await pyz3r.rom.write(patched_rom, patched_rom_filename)

    logger.info(f"Generated Hash: {seed.hash}")
    logger.info(f"Generated Code: {seed.code}")


async def fetch_preset(preset):
    logger.info(f"Loading preset {preset} from ALTTPR")
    # load default randomizer settings from alttpr
    alttpr = await pyz3r.alttpr()
    all_settings = await alttpr.randomizer_settings()
    return convert_randomizer_settings(all_settings['presets'][preset])


@click.command()
@click.option("--base-rom-filename", type=str, required=True)
@click.option("--patched-rom-filename", type=str, required=True)
@click.option("--preset", type=str, required=True)
def main(base_rom_filename, patched_rom_filename, preset):
    if preset is not None:
        settings = asyncio.run(fetch_preset(preset))

    asyncio.run(
        generate_rom(settings, base_rom_filename, patched_rom_filename))


if __name__ == '__main__':
    main()
