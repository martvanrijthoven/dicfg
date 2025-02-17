from collections import UserDict, defaultdict
from functools import reduce

from dicfg.addons.addon import (
    ADDONS,
    Addon,
    TemplateAddon,
    process_addons,
    select_addon,
)
from dicfg.addons.validators import ValidationError
from dicfg.configs.configvalue import ConfigValue


class ConfigDict(ConfigValue, UserDict[str, ConfigValue], data_type=dict):
    """Wraps a value into a ConfigDict

    Args:
        data (dict): value of the config

    """

    def _init(self, data: dict):
        for key in list(data):
            config_kwargs: dict[str, list[Addon]] = defaultdict(list)
            _key, addons = process_addons(key)
            value = data.pop(key)
            for addon, name in addons:
                config_kwargs[addon].append(select_addon(addon, name))

            templates = config_kwargs.pop(ADDONS.TEMPLATE.value, None)
            data[_key] = ConfigValue.factory(value, **config_kwargs)
            if templates is not None:
                data[_key] = self._apply_templates(data[_key], templates)

        return data

    def _apply_templates(
        self, config_value: ConfigValue, templates: list[TemplateAddon]
    ):
        """Apply templates to the given config value."""
        for template in templates:
            template_data = ConfigValue.factory(template.data())
            if isinstance(config_value, ConfigDict) and isinstance(
                template_data, ConfigDict
            ):
                config_value = template_data.modify(config_value)
            else:
                config_value = template_data

        return config_value

    def validate(self):
        yield from super().validate()
        for key, value in self.data.items():
            for err in value.validate():
                yield ValidationError(f"{key}:{err.message}")

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return {key: value.cast() for key, value in self.data.items()}


def _modify(a: ConfigValue, b: ConfigValue):
    return a.modify(b)


def merge(*args: tuple[dict]) -> ConfigDict:
    """Merges different configs

    Returns:
        ConfigDict: merged configs
    """

    return reduce(_modify, map(ConfigValue.factory, args), ConfigDict({}))
