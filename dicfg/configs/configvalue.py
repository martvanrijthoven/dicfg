from collections import UserDict
from enum import Enum
from typing import Any, Optional

from dicfg.addons.addon import ModifierAddon, UpdaterAddon, ValidatorAddon


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

    _registry = {}

    def __init_subclass__(cls, *, data_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if data_type is not None:
            ConfigValue._registry[data_type] = cls

    @classmethod
    def factory(
        cls,
        data,
        updater: list[UpdaterAddon] = None,
        validator: list[ValidatorAddon] = None,
        modifier: list[ModifierAddon] = None,
    ):

        if isinstance(data, cls):
            return data

        mods = modifier or (None,)
        for mod in mods:
            if mod is not None:
                data = mod.modify(data)

        target_cls = cls._registry.get(type(data), cls)
        return target_cls(data, updater, validator)

    def __init__(
        self,
        data: Any,
        updater: tuple[UpdaterAddon] = None,
        validator: tuple[ValidatorAddon] = None,
    ):
        self.updater = updater or (None,)
        self.validator = validator or (None,)
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


def update(a: ConfigValue, b: ConfigValue, affix: Optional[Affix] = None) -> Any:
    if not isinstance(b, UserDict):
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


def _insert(dictionary, prev_key, k, v):
    new_dict = {}
    for _k, _v in dictionary.items():
        new_dict[_k] = _v
        if prev_key == _k:
            new_dict[k] = v
    return new_dict
