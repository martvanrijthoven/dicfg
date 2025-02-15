import importlib
import inspect
from abc import ABC

from dicfg.addons.addon import ValidatorAddon
from dicfg.addons.validators import ValidationError
from dicfg.factory import OBJECT_KEY, WHITE_LIST_FACTORY_KEYS


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


class IntTypeValidator(TypeValidator):
    """
    Validator for integer type.
    """

    NAME: str = "int"
    EXPECTED_TYPE = int


class FloatTypeValidator(TypeValidator):
    """
    Validator for float type.
    """

    NAME: str = "float"
    EXPECTED_TYPE = float


class NumberTypeValidator(TypeValidator):
    """
    Validator for number type (int or float).
    """

    NAME: str = "number"
    EXPECTED_TYPE = (int, float)


class StrTypeValidator(TypeValidator):
    """
    Validator for string type.
    """

    NAME: str = "str"
    EXPECTED_TYPE = str


class BoolTypeValidator(TypeValidator):
    """
    Validator for boolean type.
    """

    NAME: str = "bool"
    EXPECTED_TYPE = bool


class ListTypeValidator(TypeValidator):
    """
    Validator for list type.
    """

    NAME: str = "list"
    EXPECTED_TYPE = list


class TupleTypeValidator(TypeValidator):
    """
    Validator for tuple type.
    """

    NAME: str = "tuple"
    EXPECTED_TYPE = tuple


class SetTypeValidator(TypeValidator):
    """
    Validator for set type.
    """

    NAME: str = "set"
    EXPECTED_TYPE = set


class DictTypeValidator(TypeValidator):
    """
    Validator for dictionary type.
    """

    NAME: str = "dict"
    EXPECTED_TYPE = dict


class SequenceTypeValidator(TypeValidator):
    """
    Validator for sequence type (list or tuple).
    """

    NAME: str = "sequence"
    EXPECTED_TYPE = (list, tuple)


class ContainerTypeValidator(TypeValidator):
    """
    Validator for container type (list, tuple, or set).
    """

    NAME: str = "container"
    EXPECTED_TYPE = (list, tuple, set)


class CollectionTypeValidator(TypeValidator):
    """
    Validator for collection type (list, tuple, set, or dict).
    """

    NAME: str = "collection"
    EXPECTED_TYPE = (list, tuple, set, dict)


class NoneTypeValidator(TypeValidator):
    """
    Validator for None type.
    """

    NAME: str = "none"
    EXPECTED_TYPE = type(None)


class ObjectTypeValidatorAddon(DictTypeValidator):
    """Validator that checks if a value is a valid object configuration"""

    NAME = "object"

    @classmethod
    def validate(cls, value: dict) -> ValidationError:
        super().validate(value)

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
