from abc import ABC, abstractmethod
from enum import Enum
import re


class CONFIG_ADDONS(Enum):
    UPDATER = "updater"
    VALIDATOR = "validator"
    TEMPLATE = "template"


_ADDON_PATTERN = r"@(\w+)\(([^)]*)\)"


def process_addons(key: str):
    addons = re.findall(_ADDON_PATTERN, key)
    # Remove all annotations from the key
    key = re.sub(_ADDON_PATTERN, "", key)
    # Strip any leading/trailing whitespace or separators (if needed)
    key = key.strip()
    return key, addons


class UnsupportedAddonError(Exception):
    """Exception raised when an unsupported addon is used"""


class Addon(ABC):
    """Base class for config validators"""

    __registry = None
    NAME = None

    def __init_subclass__(cls: "Addon", **kwargs):
        if cls.__registry is None:
            cls.__registry = {}

        if cls.NAME in cls.__registry:
            raise ValueError(f"Addon with name '{cls.NAME}' already exists.")

        cls.__registry[cls.NAME] = cls
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_addon(cls, name: str) -> "Addon":
        if name not in cls.__registry:
            raise UnsupportedAddonError(
                f"Addon {cls.NAME} with name '{name}' not found."
            )
        return cls.__registry[name]()


class TemplateAddon(Addon):
    """Template addon for config values to be used for predefined templates"""

    NAME = "template"

    @property
    @abstractmethod
    def data(self):
        """Data to be used for template"""


class ValidatorAddon(Addon):
    """Validator addon for config values to be used to validate data"""

    NAME = "validator"

    @abstractmethod
    def validate(self, value):
        """Validate the value"""


class UpdaterAddon(Addon):
    """Replace addon for config values to be used to replace or merge data"""

    NAME = "updater"

    @abstractmethod
    def update(self, a, b):
        """Update a with b"""


_ADDONS = {
    CONFIG_ADDONS.UPDATER: UpdaterAddon,
    CONFIG_ADDONS.VALIDATOR: ValidatorAddon,
    CONFIG_ADDONS.TEMPLATE: TemplateAddon,
}


def select_addon(addon: str, name: str) -> Addon:
    try:
        _addon: Addon = _ADDONS[CONFIG_ADDONS(addon)]
    except ValueError:
        raise UnsupportedAddonError(f"Addon {addon} not found.")
    return _addon.get_addon(name)
