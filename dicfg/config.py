import re
from collections import UserDict, UserList
from functools import reduce
from typing import Tuple


class _ConfigValue:
    def __init__(self, data, merger=None):
        self._merger = merger
        self.data = self._init(data)

    def _init(self, data):
        return data

    def merge(self, b: "_ConfigValue"):
        if self._merger is None and b._merger is None:
            self.data = _update(self, b)
        elif b._merger is not None:
            self.data = b._merger(self, b)
            self._merger = b._merger
        else:
            self.data = self._merger(self, b)
        return self

    def cast(self):
        return self.data


class _ConfigDict(_ConfigValue, UserDict):
    def _init(self, data: dict):
        for key in list(data):
            _key, merger = _get_merger(key, data[key])
            data[_key] = _config_factory(data.pop(key), merger=merger)
        return data

    def cast(self):
        return {key: value.cast() for key, value in self.data.items()}


class _ConfigList(_ConfigValue, UserList):
    def _init(self, data):
        for idx, value in enumerate(data):
            data[idx] = _config_factory(value)
        return data

    def cast(self):
        return [value.cast() for value in self.data]


_CONFIGS = {dict: _ConfigDict, list: _ConfigList}
_REPLACE_IDENTIFIER = r"\@replace\((.*)\)"


def _config_factory(c, merger=None):
    if isinstance(c, _ConfigValue):
        return c
    return _CONFIGS.get(type(c), _ConfigValue)(c, merger=merger)


def _update(a: _ConfigValue, b: _ConfigValue):
    if type(a) != type(b):
        raise ValueError('Can not merger different types at this level', a, b)

    if type(b) is not _ConfigDict:
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

    if type(value) is dict and replace:
        return key, lambda a, b: b.data
    elif type(value) is list and not replace:
        return key, lambda a, b: a.data + b.data
    return key, _update


def _get_replace(replace_match: re.Match):
    replace_str = replace_match.group(1).lower()
    if replace_str not in ("true", "false"):
        raise ValueError(replace_str)
    return replace_str == "true"


def _merge(a: _ConfigValue, b: _ConfigValue):
    return a.merge(b)


def merge(*args: Tuple[dict]):
    return reduce(_merge, map(_config_factory, args), _ConfigDict({}))
