import importlib
import operator
from copy import deepcopy
from functools import reduce, singledispatchmethod
from pathlib import Path
from typing import Any, Union

from dicfg.reader import ConfigReader


class ObjectConfigFactory:

    _REFERENCE_START_SYMBOL = "$"
    _REFERENCE_MAP_SYMBOL = ":"
    _REFERENCE_ATTRIBUTE_SYMBOL = "."

    CONFIG_READER = ConfigReader

    @classmethod
    def build(cls, config):
        return cls(deepcopy(config))._build_config()

    def __init__(self, config):
        self._configuration = config

    def _build_config(self):
        return self._build(self._configuration)

    @singledispatchmethod
    def _build(self, config: Any):
        return config

    @_build.register
    def _build_dict(self, config: dict):
        for key, value in config.items():
            if self._is_object(value):
                config[key] = self._build_object(value)
            else:
                config[key] = self._build(value)
        return config

    @_build.register(list)
    @_build.register(tuple)
    def _build_list(self, config: Union[list, tuple]):
        for idx, item in enumerate(config):
            if self._is_object(item):
                config[idx] = self._build_object(item)
            else:
                config[idx] = self._build(item)
        return config

    @_build.register
    def _build_str(self, config: str):
        if config.lower() == "none":
            return None
        if config[0] == self._REFERENCE_START_SYMBOL:
            return self._get_reference(reference=config)
        return config

    def _build_object(self, value: dict):
        module = _get_module(value.pop("module"))
        attributes = value.pop("attribute").split(".")
        attribute = reduce(getattr, attributes, module)
        value = self._build(value)
        if ":return_type" in value:
            return attribute
        return attribute(**value)

    def _get_reference(self, reference: str):
        reference = reference[1:].replace("{", "").replace("}", "")
        references = reference.split(self._REFERENCE_MAP_SYMBOL)
        if references[0] == self.CONFIG_READER.NAME:
            references = references[1:]
        reference = reduce(operator.getitem, references[:-1], self._configuration)
        attributes = references[-1].split(self._REFERENCE_ATTRIBUTE_SYMBOL)
        reference = reference[attributes[0]]
        for attr in attributes[1:]:
            reference = getattr(reference, attr)
        return reference

    @staticmethod
    def _is_object(value):
        return type(value) is dict and set(("module", "attribute")).issubset(set(value))


def _get_module(module):
    try:
        return importlib.import_module(module)
    except Exception:
        module = Path(module)
        spec = importlib.util.spec_from_file_location(module.stem, str(module))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
