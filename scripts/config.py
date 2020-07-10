import enum
import json
import pathlib

from dialog import Dialog
import pyz3r.rom
import pyz3r.exceptions

from textwrap import dedent

from retropie_alttpr import api, cache, randomizer_config


class Menus(enum.Enum):
    main_menu = 'Main Menu'
    select_preset_menu = 'Select Preset Menu'
    configure_current = 'Customize Configuration'
    write_configuration = 'Write Configuration'
    load_configuration = "Load Configuration"
    select_base_rom = "Select Base Zelda ROM"
    change_option = 'Change Option'


class ConfigMenu:
    def __init__(self):
        self.dialog = Dialog(autowidgetsize=True)

        self.alttpr_settings = api.fetch_randomizer_settings()
        # current config, in "preset" configuration to ease using randomizer settings dicts
        self.current_config = randomizer_config.RandomizerConfig().export_as_preset()

    def main_menu(self):
        choices = []
        for menu in [Menus.select_preset_menu,
                     Menus.configure_current,
                     Menus.write_configuration,
                     Menus.load_configuration,
                     Menus.select_base_rom]:
            choices.append((menu.name, menu.value))

        code, tag = self.dialog.menu("Select an option", choices=choices)

        if tag:
            tag = Menus[tag]

        return code, tag

    def select_base_rom(self):
        self.dialog.msgbox(dedent("""\
            The file selector is a little unintuitive.
            Double click a directory in the left pane to navigate to the folder
            containing your Japan Zelda 1.0 ROM.
            Click the file in the right pane to autofill the dialog box with the full path.
            Then press OK.
            The ROM is cached in a known location, so you should hopefully only
            need to do this once.
            """))

        code, tag = self.dialog.fselect(filepath=str(pathlib.Path("~").expanduser()), height=10, width=100)
        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return self.dialog.OK, Menus.main_menu

        if code != self.dialog.OK:
            raise Exception(f"code == {code}")

        try:
            api.validate_rom(tag)
        except pyz3r.exceptions.alttprException:
            self.dialog.msgbox("Specified rom file did not checksum for Japan Zelda 1.0")
            return self.dialog.OK, Menus.main_menu

        with open(tag, 'rb') as f:
            zelda_rom_bytes = f.read()
            cache.misc.put('base_zelda_rom', zelda_rom_bytes)

        return self.dialog.OK, Menus.main_menu

    def select_preset_menu(self):
        choices = []

        for preset in self.alttpr_settings['presets']:
            if preset == 'custom':
                continue
            choices.append((preset, preset))

        code, tag = self.dialog.menu("Select a preset", choices=choices)

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return self.dialog.OK, Menus.main_menu

        if code != self.dialog.OK:
            raise Exception(f"code == {code}")

        preset_dict = self.alttpr_settings['presets'][tag]

        # import then re-export because presets do not contain all options
        self.current_config = randomizer_config.from_preset_dict(preset_dict).export_as_preset()

        return code, Menus.main_menu

    def configure_current(self):
        while True:
            choices = []
            for name, value in self.current_config.items():
                choices.append((name, str(value)))

            code, tag = self.dialog.menu("Select an entry to modify", choices=choices)

            if code in (self.dialog.ESC, self.dialog.CANCEL):
                return self.dialog.OK, Menus.main_menu

            if code != self.dialog.OK:
                raise Exception(f"code == {code}")

            self.configure_entry(tag)

    def configure_entry(self, config_name):
        choices = []
        current_value = self.current_config[config_name]
        if config_name in self.alttpr_settings:
            for value, desc in self.alttpr_settings[config_name].items():
                choices.append((value, desc, value == current_value))

            code, tag = self.dialog.radiolist("Choose a value", choices=choices)

            if code in (self.dialog.ESC, self.dialog.CANCEL):
                return

            if code != self.dialog.OK:
                raise Exception(f"code == {code}")

            self.current_config[config_name] = tag
        else:
            raise Exception("Unhandled config type")

    def write_configuration(self):
        choices = [(c, c) for c in ["alpha", "beta", "gamma", "delta"]]

        code, tag = self.dialog.menu("Choose a file to write", choices=choices)

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        if code != self.dialog.OK:
            raise Exception(f"code == {code}")

        cache.config.put(tag, cache.json_encode_to_bytes(self.current_config))

        return self.dialog.OK, Menus.main_menu

    def load_configuration(self):
        choices = [(c, c) for c in ["alpha", "beta", "gamma", "delta"]]

        code, tag = self.dialog.menu("Choose a file to read", choices=choices)

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        if code != self.dialog.OK:
            raise Exception(f"code == {code}")

        self.current_config = json.loads(cache.config.get(tag))

        return self.dialog.OK, Menus.main_menu

    def driver(self):
        menus = {
            Menus.main_menu: self.main_menu,
            Menus.select_preset_menu: self.select_preset_menu,
            Menus.configure_current: self.configure_current,
            Menus.write_configuration: self.write_configuration,
            Menus.load_configuration: self.load_configuration,
            Menus.select_base_rom: self.select_base_rom,
            }

        code, tag = self.dialog.OK, Menus.main_menu,
        while code == self.dialog.OK:
            code, tag = menus[tag or Menus.main_menu]()


def main():
    ConfigMenu().driver()


if __name__ == '__main__':
    main()
