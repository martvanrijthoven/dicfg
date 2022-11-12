import operator
import re
from copy import deepcopy
from functools import reduce, singledispatchmethod
from importlib import import_module
from typing import Any, Union


class ObjectFactory:
    """Allows for building configs
    """

    _REFERENCE_START_SYMBOL = "$"
    _REFERENCE_MAP_SYMBOL = ":"
    _REFERENCE_ATTRIBUTE_SYMBOL = "."

    _OBJECT_KEY = "*object"
    _RETURN_TYPE_KEY = "*return_type"

    @classmethod
    def build(cls, config: dict):
        """Builds a config

        Args:
            config (dict): config to be build

        Returns:
            dict: build config 
        """

        return cls(deepcopy(config))._build_config()

    def __init__(self, config: dict):
        """Initialize with config 

        Args:
            config (dict): config dictionary
        """

        self._configuration = config

    def _build_config(self):
        return self._build(self._configuration)

    @singledispatchmethod
    def _build(self, config: dict):
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
        if self._REFERENCE_START_SYMBOL in config:
            return self._get_reference(reference=config)
        return config

    def _build_object(self, value: dict):
        kwargs = self._build(value)
        args = [] if '*args' not in kwargs else value.pop("*args")
        object = value.pop(ObjectFactory._OBJECT_KEY)
        attribute = self._parse_object_str(object)

        if ObjectFactory._RETURN_TYPE_KEY in value:
            return attribute
        return attribute(*args, **kwargs)

    def _parse_object_str(self, object: str):
        object = object.split(".")
        module_string = ".".join(object[:-1])
        attribute_string = object[-1]
        module = import_module(module_string)
        return getattr(module, attribute_string)

    def _get_reference(self, reference: str):
        matches = re.findall("\\${(.*?)}", reference)
        if matches == 1 or len(matches[0]) + 3 == len(reference):
            return self._object_interpolation(reference, matches)
        return self._string_interpolation(reference, matches)

    def _object_interpolation(self, reference, matches):
        reference = matches[0]
        references = reference.split(self._REFERENCE_MAP_SYMBOL)
        reference = reduce(operator.getitem, references[:-1], self._configuration)
        attributes = references[-1].split(self._REFERENCE_ATTRIBUTE_SYMBOL)
        reference = reference[attributes[0]]
        for attr in attributes[1:]:
            reference = getattr(reference, attr)
        return reference

    def _string_interpolation(self, reference, matches):
        for match in matches:
            _reference = self._configuration[match]
            match = "${" + match + "}"
            reference = reference.replace(match, str(_reference))
        return reference

    @staticmethod
    def _is_object(value):
        object_key_set = set((ObjectFactory._OBJECT_KEY,))
        return isinstance(value, dict) and object_key_set.issubset(set(value))
