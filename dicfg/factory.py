import operator
import os
import re
from copy import deepcopy
from functools import reduce, singledispatchmethod
from importlib import import_module
from typing import Union
from dicfg.addons.templates import LogLevel

REFERENCE_START_SYMBOL = "$"
REFERENCE_MAP_SYMBOL = ":"
REFERENCE_ATTRIBUTE_SYMBOL = "."

OBJECT_KEY = "*object"
ARGS_KEY = "*args"
KWARGS_KEY = "**kargs"
BUILD_KEY = "*build"
LOG_KEY = "*log"

WHITE_LIST_FACTORY_KEYS = [OBJECT_KEY, ARGS_KEY, KWARGS_KEY, BUILD_KEY, LOG_KEY]


class InvalidObjectConfigurationError(Exception):
    """Custom exception for invalid object configuration errors."""

    pass


class InvalidReferenceError(Exception):
    """Custom exception for invalid reference errors."""

    pass


class _ObjectFactory:
    def __init__(self, config: dict):
        self._configuration = config

        self._re_pattern_map = {
            "\\${\\$env.(.*)}": os.environ.get,
            "\\${\\$(.*)}": self._parse_object_str,
        }

    def build_config(self):
        return self._build(self._configuration)

    @singledispatchmethod
    def _build(self, config: dict):
        return config

    @_build.register
    def _build_dict(self, config: dict):
        for key, value in config.items():
            if not _build(value):
                config[key] = value
                continue

            if _is_object_config(value):
                self._logging(value, key)
                config[key] = self._build_object(value)
            else:
                config[key] = self._build(value)

        return config

    def _logging(self, value: dict, key: str):
        """Handle logging based on the configuration value."""
        if log := value.pop(LOG_KEY, False):
            if log == LogLevel.VERBOSE:
                print("\tRunning:", key)
            elif log == LogLevel.DEBUG:
                print("\tRunning:", key)
                print("\tConfig:", value)
            else:
                raise ValueError(f"Invalid log level: {log}")

    @_build.register(list)
    @_build.register(tuple)
    def _build_list(self, config: Union[list, tuple]):
        for idx, item in enumerate(config):
            if _is_object_config(item):
                config[idx] = self._build_object(item)
            else:
                config[idx] = self._build(item)
        return config

    @_build.register
    def _build_str(self, config: str):
        if config.lower() == "none":
            return None
        if REFERENCE_START_SYMBOL in config:
            return self._get_reference(reference=config)
        return config

    def _build_object(self, value: dict):
        try:
            kwargs = self._build(value)
            object_string = value.pop(OBJECT_KEY)
            args = value.pop(ARGS_KEY, ())
            kwargs.update(value.pop(KWARGS_KEY, {}))
            attribute = self._parse_object_str(object_string)
            return attribute(*args, **kwargs)
        except (ModuleNotFoundError, AttributeError, TypeError) as e:
            raise InvalidObjectConfigurationError(
                f"Invalid object configuration:\nObject: {object_string}\nArgs: {value}\nError: {e}"
            ) from e

    def _parse_object_str(self, object_string: str):
        object_split = object_string.split(".")
        module_string = ".".join(object_split[:-1])
        attribute_string = object_split[-1]
        module = import_module(module_string)
        return getattr(module, attribute_string)

    def _get_reference(self, reference: str):
        try:
            for pattern, parse in self._re_pattern_map.items():
                match = re.fullmatch(pattern, reference)
                if match is not None:
                    return parse(match.group(1))

            matches = re.findall("\\${(.*?)}", reference)
            if len(matches) == 1 and len(matches[0]) + 3 == len(reference):
                return self._object_interpolation(matches[0])
            return self._string_interpolation(reference, matches)
        except (IndexError, KeyError, AttributeError):
            raise InvalidReferenceError(reference)

    def _object_interpolation(self, reference: str):
        references = reference.split(REFERENCE_MAP_SYMBOL)
        reference = reduce(operator.getitem, references[:-1], self._configuration)
        attributes = references[-1].split(REFERENCE_ATTRIBUTE_SYMBOL)
        reference = reference[attributes[0]]
        for attr in attributes[1:]:
            reference = getattr(reference, attr)
        return reference

    def _string_interpolation(self, reference, matches):
        for match in matches:
            _reference = self._object_interpolation(match)
            match = "${" + match + "}"
            reference = reference.replace(match, str(_reference))
        return reference


def _is_object_config(value):
    return isinstance(value, dict) and OBJECT_KEY in value


def _build(value):
    if isinstance(value, dict):
        return value.pop(BUILD_KEY, True)
    return True


def build_config(config: dict):
    """Builds config

    Args:
        config (dict): config to build

    Returns:
        dict: build config
    """

    return _ObjectFactory(deepcopy(config)).build_config()
