from collections import UserDict, UserList
from functools import reduce
from typing import Any, Optional, Tuple

from dicfg.addons.addons import (
    CONFIG_ADDONS,
    Addon,
    TemplateAddon,
    UpdaterAddon,
    ValidatorAddon,
    process_addons,
    select_addon,
)
from dicfg.addons.validators import ValidationError


class ConfigValue:
    """Wraps a value into a ConfigValue

    Args:
        data (Any): value of the config
        merger (Callable, optional): Callable to merge the config value. Defaults to None.
    """

    def __init__(
        self,
        data: Any,
        updater: UpdaterAddon = None,
        validator: ValidatorAddon = None,
    ):
        self.updater = updater
        self.validator = validator
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

        if self.updater is None and b.updater is None:
            self.data = update(self, b)
        elif b.updater is not None:
            self.data = b.updater.update(self, b)
        else:
            self.data = self.updater.update(self, b)
        return self

    def validate(self):
        """Validate the config"""
        if self.validator is not None:
            if error := self.validator.validate(self.data):
                yield error

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return self.data


class ConfigDict(ConfigValue, UserDict):
    """Wraps a value into a ConfigDict

    Args:
        data (dict): value of the config

    """

    def _init(self, data: dict):
    
        for key in list(data):
            config_kwargs: dict[str, Addon] = {}
            template: Optional[TemplateAddon] = None

            _key, addons = process_addons(key)
            value = data.pop(key)
            for addon, name in addons:
                config_kwargs[addon] = select_addon(addon, name)

            template = config_kwargs.pop(CONFIG_ADDONS.TEMPLATE.value, None)
            data[_key] = _config_factory(value, **config_kwargs)

            if template is not None:
                template_data = _config_factory(template.data)
                if not isinstance(data[_key], type(template_data)):
                    data[_key] = template_data
                else:
                    data[_key] = template_data.modify(data[_key])
        return data

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


def _config_factory(c, updater=None, validator=None) -> ConfigValue:
    if isinstance(c, ConfigValue):
        return c
    config_types = {dict: ConfigDict, list: ConfigList}
    return config_types.get(type(c), ConfigValue)(
        c, updater=updater, validator=validator
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


def update(a: ConfigValue, b: ConfigValue):
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
            if prev_key is None:
                a.data = {**a.data, **{k: v}}
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
