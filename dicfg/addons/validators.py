from dataclasses import dataclass
import importlib

import inspect

from dicfg.addons.addons import ValidatorAddon
from dicfg.factory import WHITE_LIST_FACTORY_KEYS, OBJECT_KEY


@dataclass(frozen=True)
class ValidationError:
    message: str

class ValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "\n".join(str(err) for err in self.errors)


class RequiredValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "required"

    def validate(self, value):
        if not (value != "" and value is not None):
            return ValidationError("Value is required and must not be empty or None.")

class DepreciatedValidatorAddon(ValidatorAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "depreciated"

    def validate(self, value):
        if not (value == "" or value is None):
            return ValidationError("Value is depreciated and should not be used")


class ObjectValidatorAddon(ValidatorAddon):
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
