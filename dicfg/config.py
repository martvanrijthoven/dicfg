import re
from collections import UserDict, UserList
from functools import reduce
from typing import Any, Callable, Tuple

from dicfg.validators import ConfigValidator, ValidationError

_VALIDATION_PATTERN = r"\@validate\((.*)\)"
_REPLACE_PATTERN = r"\@replace\((.*)\)"


class ConfigValue:
    """Wraps a value into a ConfigValue

    Args:
        data (Any): value of the config
        merger (Callable, optional): Callable to merge the config value. Defaults to None.
    """

    def __init__(
        self, data: Any, merger: Callable = None, validator: ConfigValidator = None
    ):
        self.merger = merger
        self.validator = validator
        self.data = self._init(data)

    def _init(self, data):
        return data

    def merge(self, b: "ConfigValue") -> "ConfigValue":
        """Merges config b with it self

        Args:
            b (ConfigValue): another config

        Returns:
            ConfigValue: self
        """

        if self.merger is None and b.merger is None:
            self.data = _update(self, b)
        elif b.merger is not None:
            self.data = b.merger(self, b)
        else:
            self.data = self.merger(self, b)
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
            _key, merger = _get_merger(key, data[key])
            _key, validator = _get_validator(_key)

            data[_key] = _config_factory(
                data.pop(key), merger=merger, validator=validator
            )
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


def _config_factory(c, merger=None, validator=None):
    if isinstance(c, ConfigValue):
        return c
    config_types = {dict: ConfigDict, list: ConfigList}
    return config_types.get(type(c), ConfigValue)(c, merger=merger, validator=validator)


def _update(a: ConfigValue, b: ConfigValue):
    if not isinstance(b, ConfigDict):
        return b.data

    prev_key = None
    for k, v in b.items():
        if k in a:
            if type(b[k]) != type(a[k]):  # noqa: E721
                a[k] = b[k]
            else:
                a[k].merge(v)
        else:
            if prev_key is None:
                a.data = {**a.data, **{k: v}}
            else:
                a.data = _insert(a, prev_key, k, v)
        prev_key = k
    return a.data


def _get_validator(key: str):
    validation_match = re.search(_VALIDATION_PATTERN, key)
    if validation_match is None:
        return key, None

    key = key.replace(validation_match.group(0), "")
    validator_str = validation_match.group(1)
    validator = ConfigValidator.get_validator(validator_str)
    return key, validator


def _get_merger(key: str, value):
    replace_match = re.search(_REPLACE_PATTERN, key)
    if replace_match is None:
        return key, None

    key = key.replace(replace_match.group(0), "")
    replace = _get_replace(replace_match)

    if isinstance(value, dict) and replace:
        return key, lambda a, b: b.data
    if isinstance(value, list) and not replace:
        return key, lambda a, b: a.data + b.data
    return key, _update


def _get_replace(replace_match: re.Match):
    replace_str = replace_match.group(1).lower()
    if replace_str not in ("true", "false"):
        raise ValueError(replace_str)
    return replace_str == "true"


def _merge(a: ConfigValue, b: ConfigValue):
    return a.merge(b)


def _insert(dictionary, prev_key, k, v):
    new_dict = {}
    for _k, _v in dictionary.items():
        new_dict[_k] = _v
        if prev_key == _k:
            new_dict[k] = v
    return new_dict


def merge(*args: Tuple[dict]) -> ConfigDict:
    """Merges different configs

    Returns:
        ConfigDict: merged configs
    """

    return reduce(_merge, map(_config_factory, args), ConfigDict({}))
