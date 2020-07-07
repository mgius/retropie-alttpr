import asyncio
import pyz3r

from dialog import Dialog

from retropie_alttpr import util


async def main():
    d = Dialog()
    d.msgbox("Loading presets from ALTTPR website")

    presets = await util.fetch_presets()

    choices = [(preset_name, preset_name) 
               for preset_name in presets]

    code, tag = d.menu("Select a preset",
                        choices=choices)
    print(f"{code}: {tag}")



if __name__ == '__main__':
    asyncio.run(main())
