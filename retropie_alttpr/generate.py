import asyncio
import pyz3r

import click

from loguru import logger


def convert_randomizer_settings(web_dict):
    """
    Convert web/JS randomizer presets to API compatible presets

    There is no API from ALTTPR website to provide API compatible generation
    configs.  There is, however, an API for web/JS compatible presets.  This
    method converts those presets so that they can be used with this library.
    """
    return {
            "glitches": web_dict.get("glitches_required"),
            "item_placement": web_dict.get("item_placement"),
            "dungeon_items": web_dict.get("dungeon_items"),
            "accessibility": web_dict.get("accessibility"),
            "goal": web_dict.get("goal"),
            "crystals": {
                "ganon": web_dict.get("ganon_open"),
                "tower": web_dict.get("tower_open"),
                },
            "mode": web_dict.get("world_state"),
            "entrances": web_dict.get("entrance_shuffle"),
            "hints": web_dict.get("hints"),
            "weapons": web_dict.get("weapons"),
            "item": {
                "pool": web_dict.get("item_pool"),
                "functionality": web_dict.get("item_functionality"),
                },
            "lang": "en",
            "enemizer": {
                "boss_shuffle": web_dict.get("boss_shuffle"),
                "enemy_shuffle": web_dict.get("enemy_shuffle"),
                "enemy_damage": web_dict.get("enemy_damage"),
                "enemy_health": web_dict.get("enemy_health"),
                }
           }


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
