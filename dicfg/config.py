import re
from collections import UserDict, UserList
from functools import reduce
from typing import Any, Callable, Tuple


_REPLACE_IDENTIFIER = r"\@replace\((.*)\)"


class ConfigValue:
    """Wrapper config for values"""

    def __init__(self, data: Any, merger: Callable = None):
        """Wraps a value into a Config

        Args:
            data (Any): value of the config
            merger (Callable, optional): Callable to merge the config value. Defaults to None.
        """
        self.merger = merger
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
            self.merger = b.merger
        else:
            self.data = self.merger(self, b)
        return self

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return self.data


class ConfigDict(ConfigValue, UserDict):
    """Wrapper config for dict"""

    def _init(self, data: dict):
        """_summary_

        Args:
            data (dict): value of the config

        """
        for key in list(data):
            _key, merger = _get_merger(key, data[key])
            data[_key] = _config_factory(data.pop(key), merger=merger)
        return data

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return {key: value.cast() for key, value in self.data.items()}


class ConfigList(ConfigValue, UserList):
    def _init(self, data: list):
        """_summary_

        Args:
            data (list): value of the config

        """

        for idx, value in enumerate(data):
            data[idx] = _config_factory(value)
        return data

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return [value.cast() for value in self.data]


def _config_factory(c, merger=None):
    if isinstance(c, ConfigValue):
        return c
    _configs = {dict: ConfigDict, list: ConfigList}
    return _configs.get(type(c), ConfigValue)(c, merger=merger)


def _update(a: ConfigValue, b: ConfigValue):
    if not isinstance(b,ConfigDict):
        return b.data

    for k, v in b.items():
        if k in a:
            # merge different types
            if type(a[k]) != type(b[k]):
                a[k] = b[k]
            else:
                a[k].merge(v)
        else:
            a[k] = v
    return a.data


def _get_merger(key: str, value):
    replace_match = re.search(_REPLACE_IDENTIFIER, key)
    if replace_match is None:
        return key, None

    key = key.replace(replace_match.group(0), "")
    replace = _get_replace(replace_match)

    if isinstance(value, dict) and replace:
        return key, lambda a, b: b.data
    elif isinstance(value, list) and not replace:
        return key, lambda a, b: a.data + b.data
    return key, _update


def _get_replace(replace_match: re.Match):
    replace_str = replace_match.group(1).lower()
    if replace_str not in ("true", "false"):
        raise ValueError(replace_str)
    return replace_str == "true"


def _merge(a: ConfigValue, b: ConfigValue):
    return a.merge(b)


def merge(*args: Tuple[dict]) -> ConfigDict:
    """Merges different configs

    Returns:
        ConfigDict: merged configs
    """

    return reduce(_merge, map(_config_factory, args), ConfigDict({}))
