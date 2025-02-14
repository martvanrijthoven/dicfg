from collections import UserDict, UserList
from functools import reduce
from typing import Any, Optional, Tuple
from enum import Enum
from collections import defaultdict

from dicfg.addons.addon import (
    CONFIG_ADDONS,
    Addon,
    ModifierAddon,
    TemplateAddon,
    UpdaterAddon,
    ValidatorAddon,
    process_addons,
    select_addon,
)
from dicfg.addons.validators import ValidationError


class Affix(Enum):
    """Affixes for the update function"""

    PRE = "pre"
    POST = "post"


class ConfigValue:
    """Wraps a value into a ConfigValue

    Args:
        data (Any): value of the config
        merger (Callable, optional): Callable to merge the config value. Defaults to None.
    """

    def __init__(
        self,
        data: Any,
        updater: tuple[UpdaterAddon] = None,
        validator: tuple[ValidatorAddon] = None,
        modifier: tuple[ModifierAddon] = None,
    ):
        self.updater = updater or (None,)
        self.validator = validator or (None,)
        self.modifier = modifier or (None,)
        
        for mod in self.modifier:
            if mod is not None:
                data = mod.modify(data)

        self.data = self._init(data)

    def _init(self, data):
        return data

    def modify(self, b: "ConfigValue") -> "ConfigValue":
        """Merges config b with it self

        Args:
            b (ConfigValue): another config

        Returns:
            ConfigValue: self
        """

        for idx, updater in enumerate(self.updater):
            if updater is None and b.updater[idx] is None:
                self.data = update(self, b)
            elif b.updater[idx] is not None:
                self.data = b.updater[idx].update(self, b)
            else:
                self.data = updater.update(self, b)
        return self

    def validate(self):
        """Validate the config"""
        for validator in self.validator:
            if validator is not None:
                if error := validator.validate(self.data):
                    yield error

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return self.data


class ConfigDict(ConfigValue, UserDict[str, ConfigValue]):
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

            templates = config_kwargs.pop(CONFIG_ADDONS.TEMPLATE.value, None)
            data[_key] = _config_factory(value, **config_kwargs)
            if templates is not None:
                data[_key] = self._apply_templates(data[_key], templates)

        return data

    def _apply_templates(
        self, config_value: ConfigValue, templates: list[TemplateAddon]
    ):
        """Apply templates to the given config value."""
        for template in templates:
            template_data = _config_factory(template.data())
            if isinstance(config_value, ConfigDict) and isinstance(template_data, ConfigDict):
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


class ConfigList(ConfigValue, UserList):
    """Wraps a value into a ConfigList

    Args:
        data (list): value of the config

    """

    def _init(self, data: list):
        for idx, value in enumerate(data):
            data[idx] = _config_factory(value)
        return data

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return [value.cast() for value in self.data]


def _config_factory(c, updater=None, validator=None, modifier=None) -> ConfigValue:
    if isinstance(c, ConfigValue):
        return c
    config_types = {dict: ConfigDict, list: ConfigList}
    return config_types.get(type(c), ConfigValue)(
        c, updater=updater, validator=validator, modifier=modifier
    )


def _insert(dictionary, prev_key, k, v):
    new_dict = {}
    for _k, _v in dictionary.items():
        new_dict[_k] = _v
        if prev_key == _k:
            new_dict[k] = v
    return new_dict


def _modify(a: ConfigValue, b: ConfigValue):
    return a.modify(b)


def update(a: ConfigValue, b: ConfigValue, affix: Optional[Affix] = None) -> Any:
    if not isinstance(b, ConfigDict):
        return b.data

    prev_key = None
    for k, v in b.items():
        if k in a:
            if type(b[k]) != type(a[k]):  # noqa: E721
                a[k] = b[k]
            else:
                a[k].modify(v)
        else:
            if affix == Affix.PRE:
                a.data = {k: v, **a.data}
            elif affix == Affix.POST:
                a.data = {**a.data, k: v}
            elif prev_key is None:
                a.data = {**a.data, k: v}
            else:
                a.data = _insert(a, prev_key, k, v)
        prev_key = k
    return a.data


def merge(*args: Tuple[dict]) -> ConfigDict:
    """Merges different configs

    Returns:
        ConfigDict: merged configs
    """

    return reduce(_modify, map(_config_factory, args), ConfigDict({}))
