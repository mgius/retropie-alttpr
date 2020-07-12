import json
import os

import pyz3r.patch
from dialog import Dialog

from retropie_alttpr import api, cache, randomizer_config, util


class GenerateMenu:
    def __init__(self):
        self.dialog = Dialog(autowidgetsize=True)

    def patch_from_seed(self, seed_data: dict) -> bytes:
        # pyz3r wants a list of bytes
        base_rom = list(cache.misc.get('base_zelda_rom'))
        base_patch = cache.base_patch.get(seed_data['current_rom_hash'])
        randomizer_patch = seed_data['patch']

        base_patched_rom = pyz3r.patch.apply_bps(base_rom, base_patch)
        extended_rom = pyz3r.patch.expand(base_patched_rom, seed_data['size'])
        randomized_rom = pyz3r.patch.apply(extended_rom, randomizer_patch)
        final_rom = pyz3r.patch.apply(extended_rom, pyz3r.patch.checksum(randomized_rom))

        return bytes(final_rom)

    def get_seed_for_config_name(self, config_name):
        loaded_config = json.loads(cache.config.get(config_name))
        seed_config = randomizer_config.to_seed_gen_dict(
                randomizer_config.from_preset_dict(loaded_config))

        return api.generate_seed(settings=seed_config)

    def driver(self):
        choices = [(c, c) for c in ["alpha", "beta", "gamma", "delta"]]

        code, tag = self.dialog.menu("Choose a config to generate and execute", choices=choices)

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        if code != self.dialog.OK:
            raise Exception(f"code == {code}")

        loaded_config = json.loads(cache.config.get(tag))
        seed_config = randomizer_config.from_preset_dict(loaded_config)
        seed_config_dict = randomizer_config.to_seed_gen_dict(seed_config)
        rom = api.generate_rom(seed_config_dict)

        write_to = util.in_memory_tempfile(delete=False)
        write_to.write(rom)
        write_to.close()

        os.execv("/opt/retropie/supplementary/runcommand/runcommand.sh",
                 "0", "_SYS_", "snes", write_to.name)

        raise Exception("Failed to Exec")


def main():
    GenerateMenu().driver()


if __name__ == '__main__':
    main()
