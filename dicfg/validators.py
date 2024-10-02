import abc
from dataclasses import dataclass
import importlib
from numbers import Number

import inspect

from dicfg.factory import WHITE_LIST_FACTORY_KEYS, OBJECT_KEY


@dataclass(frozen=True)
class ValidationError:
    message: str


class UnsupportedValidatorError(ValueError): ...


class ValidationErrors(Exception):
    """Exception raised when validation errors occur"""

    def __init__(self, errors: list[ValidationError]):
        formatted_errors = "\n".join([err.message for err in errors])
        super().__init__(f"\n{formatted_errors}")


class ConfigValidator(abc.ABC):
    """Base class for config validators"""

    _registry = {}
    NAME = None
    MESSAGE = "Base validation error"

    def __init_subclass__(cls: "ConfigValidator", **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "NAME"):
            if cls.NAME in ConfigValidator._registry:
                raise ValueError(f"Validator with name '{cls.NAME}' already exists.")
            ConfigValidator._registry[cls.NAME] = cls
        else:
            raise AttributeError(f"Class {cls.__name__} must define a NAME attribute")

    @abc.abstractmethod
    def validate(self, value) -> ValidationError:
        """Validate a value"""

    @classmethod
    def get_validator(cls, name: str) -> "ConfigValidator":
        if name not in cls._registry:
            raise UnsupportedValidatorError(f"Validator with name '{name}' not found.")
        return cls._registry[name]()


class ConfigNotEmptyValidator(ConfigValidator):
    """Validator that checks if a value is not empty or None"""

    NAME = "not-empty"

    def validate(self, value):
        if not (value != "" and value is not None):
            return ValidationError("Value must not be empty or None.")


class ConfigPositiveNumberValidator(ConfigValidator):
    """Validator that checks if a value is a positive number"""

    NAME = "positive-number"

    def validate(self, value):
        if not (isinstance(value, Number) and value >= 0):
            return ValidationError("Value must be a positive number.")


class ConfigPositiveNumberListValidator(ConfigValidator):
    """Validator that checks if a value is a positive number"""

    NAME = "positive-number-list"

    def validate(self, value):
        if not (isinstance(value, list) and all(v.cast() >= 0 for v in value)):
            return ValidationError("Value must be a list with only positive numbers.")


class ConfigObjectValidator(ConfigValidator):
    """Validator that checks if a value is a valid object configuration"""

    NAME = "object"

    def validate(self, value: dict) -> ValidationError:
        if not isinstance(value, dict):
            return ValidationError("Value must be a dictionary.")

        if OBJECT_KEY not in value:
            return ValidationError(
                f"The key {OBJECT_KEY} must be present in the configuration."
            )

        object_path = value[OBJECT_KEY].cast()
        try:
            module_name, object_name = object_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            obj = getattr(module, object_name)
            if not callable(obj):
                return ValidationError(f"'{object_path}' is not callable.")
        except (ImportError, AttributeError, ValueError) as e:
            return ValidationError(
                f"Failed to import or access callable for {OBJECT_KEY}: {str(e)}"
            )

        sig = inspect.signature(obj)

        remaining_keys = {
            key: value[key] for key in value if key not in WHITE_LIST_FACTORY_KEYS
        }

        for key in remaining_keys:
            if key not in sig.parameters:
                return ValidationError(
                    f"'{key}' is not a valid argument for '{object_path}'."
                )
