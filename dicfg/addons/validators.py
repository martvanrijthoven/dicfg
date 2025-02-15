from dataclasses import dataclass

from dicfg.addons.addon import ValidatorAddon


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
    """Validator"""

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
