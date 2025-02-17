from dicfg.addons.addon import ModifierAddon, UpdaterAddon, ValidatorAddon
from dicfg.configs.configvalue import ConfigValue


def create_config(
    data,
    updater: list[UpdaterAddon] = None,
    validator: list[ValidatorAddon] = None,
    modifier: list[ModifierAddon] = None,
) -> ConfigValue:
    mods = modifier or (None,)
    for mod in mods:
        if mod is not None:
            data = mod.modify(data)

    if isinstance(data, ConfigValue):
        return data

    target_cls = ConfigValue._registry.get(type(data), ConfigValue)
    return target_cls(data, updater, validator)
