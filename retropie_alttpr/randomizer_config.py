""" dataclasses for randomizer config.

usage

config = randomizer_config.RandomizerConfig()
config.weapon_state = 'assured'
seed = await pyz3r.alttpr(settings=randomizer_config.to_seed_gen_dict(config))

The real value of these classes is using it to convert freely between the dicts
used by seed generation, "presets" and spoiler meta.

seed generation format is used as the canonical format
"""


# {
#  # regular
#  'accessibility': 'items',
#  'dungeon_items': 'standard',
#  'entrance_shuffle': 'none',
#  'glitches_required': 'none',
#  'goal': 'ganon',
#  'hints': 'on',
#  'item_functionality': 'normal',
#  'weapons': 'randomized',
#  'world_state': 'open',
#  # enemizer
#  'boss_shuffle': 'none',
#  'enemy_damage': 'default',
#  'enemy_health': 'default'
#  'enemy_shuffle': 'none',
#  # crystals
#  'ganon_open': '7',
#  'tower_open': '7',
#  # items
#  'item_placement': 'advanced',
#  'item_pool': 'normal',
#  }


import abc
from dataclasses import asdict, dataclass, field, replace, fields

from typing import List, Generic, TypeVar

GenericBaseConfig = Generic[TypeVar['BaseConfig']]


@dataclass
class FieldMapping:
    target_name: str
    source_name: str


FieldMappings = List[FieldMapping]


@dataclass
class BaseConfig(abc.ABC):
    def get_preset_field_mappings(cls) -> FieldMappings:
        out = []
        for fld in fields(cls):
            target_name = fld.name
            source_name = fld.metadata.get('override_preset', target_name)
            out.append(
                FieldMapping(target_name=target_name, source_name=source_name))

        return out

    def replace_from_preset(
            self: GenericBaseConfig,
            preset) -> GenericBaseConfig:
        field_mappings = self.get_preset_field_mappings()
        updates = {}

        for config_name, preset_name in field_mappings:
            if preset_name in preset:
                updates[config_name] = preset[preset_name]

        return replace(self, **updates)


@dataclass
class CrystalConfig(BaseConfig):
    # serverside these seem to be interchangably int or str, and str is used
    # because "random" is a value
    ganon: str = field("7", metadata={'override_preset': 'ganon_open'})
    tower: str = field("7", metadata={'override_preset': 'tower_open'})


@dataclass
class ItemConfig(BaseConfig):
    functionality: str = field(
        "normal", metadata={'override_preset': 'item_functionality'})
    pool: str = field(
        "normal", metadata={'override_preset': 'item_pool'})


@dataclass
class EnemizerConfig(BaseConfig):
    boss_shuffle: str = "none"
    enemy_damage: str = "default"
    enemy_health: str = "default"
    enemy_shuffle: str = "none"


@dataclass
class RandomizerConfig(BaseConfig):
    accessibility: str = "items"
    dungeon_items: str = "standard"
    entrances: str = field(
        "none", metadata={'override_preset': 'entrance_shuffle'})
    glitches: str = field(
        "none", metadata={'override_preset': 'glitches_required'})
    goal: str = "ganon"
    hints: str = "on"
    item_placement: str = "advanced"
    lang: str = "en"
    mode: str = field("open", metadata={'override_preset': 'world_state'})
    spoilers: str = "off"
    tournament: bool = True
    weapons: str = "randomized"

    crystals: CrystalConfig = field(default_factory=CrystalConfig)
    item: ItemConfig = field(default_factory=ItemConfig)
    enemizer: EnemizerConfig = field(default_factory=EnemizerConfig)


def from_seed_gen_dict(seed_gen_dict: dict) -> RandomizerConfig:
    return RandomizerConfig(**seed_gen_dict)


def to_seed_gen_dict(config: RandomizerConfig) -> dict:
    return asdict(config)


def from_preset_dict(preset_dict: dict) -> RandomizerConfig:
    config = RandomizerConfig()
    config = config.replace_from_preset(preset_dict)
    config.crystals = config.crystals.replace_from_preset(preset_dict)
    config.item = config.item.replace_from_preset(preset_dict)
    config.enemizer = config.enemizer.replace_from_preset(preset_dict)
    return config
