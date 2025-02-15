from dataclasses import dataclass
import importlib
from abc import ABC
import inspect

from dicfg.addons.addon import ValidatorAddon
from dicfg.factory import WHITE_LIST_FACTORY_KEYS, OBJECT_KEY


@dataclass(frozen=True)
class ValidationError:
    message: str


class ValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "\n".join(str(err) for err in self.errors)


class DependenciesAddon(ValidatorAddon):
    NAME = "dependencies"


class AssignedValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "assigned"

    @classmethod
    def validate(cls, value):
        if not (value == "" or value is None):
            return ValidationError("Value is assigned and must not be set by user")


class RequiredValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "required"

    @classmethod
    def validate(cls, value):
        if not (value != "" and value is not None):
            return ValidationError("Value is required and must not be empty or None.")


class DepreciatedValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "depreciated"

    @classmethod
    def validate(cls, value):
        if not (value == "" or value is None):
            return ValidationError("Value is depreciated and should not be used")


class ObjectValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is a valid object configuration"""

    NAME = "object"

    @classmethod
    def validate(cls, value: dict) -> ValidationError:
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


class TypeValidator(ValidatorAddon, ABC):
    """
    Base class for type validators.

    Subclasses must define:
      - EXPECTED_TYPE: The type (or tuple of types) that is expected.
      - NAME: The identifier for the validator.
    """

    EXPECTED_TYPE = None  # Must be overridden in subclasses.
    NAME = "type"

    @classmethod
    def validate(cls, value):
        if not isinstance(value, cls.EXPECTED_TYPE):
            return ValidationError(
                f"Validator '{cls.NAME}': Value {value!r} is not of type {cls.EXPECTED_TYPE.__name__}."
            )
        return None


class IntValidator(TypeValidator):
    NAME = "int"
    EXPECTED_TYPE = int


class FloatValidator(TypeValidator):
    NAME = "float"
    EXPECTED_TYPE = float


class StrValidator(TypeValidator):
    NAME = "str"
    EXPECTED_TYPE = str


class BoolValidator(TypeValidator):
    NAME = "bool"
    EXPECTED_TYPE = bool


class ListValidator(TypeValidator):
    NAME = "list"
    EXPECTED_TYPE = list


class DictValidator(TypeValidator):
    NAME = "dict"
    EXPECTED_TYPE = dict


class NoneValidator(TypeValidator):
    NAME = "none"
    EXPECTED_TYPE = type(None)
