import asyncio

import click

from retropie_alttpr import api, util


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
