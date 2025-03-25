import datetime
import platform
import uuid
from enum import Enum
from pathlib import Path

from dicfg.addons.addon import TemplateAddon
from dicfg.addons.modifiers import IncludeModifierError
from dicfg.formats import FORMAT_READERS


class LogLevel(Enum):
    """Log level for templates"""

    DEBUG = "DEBUG"
    VERBOSE = "VERBOSE"


class VerboseTemplate(TemplateAddon):
    NAME = "verbose"

    @classmethod
    def data(self):
        return {"*log": LogLevel.VERBOSE}


class DebugTemplate(TemplateAddon):
    NAME = "debug"

    @classmethod
    def data(self):
        return {"*log": LogLevel.DEBUG}


class BuildTemplate(TemplateAddon):
    NAME = "build"

    @classmethod
    def data(self):
        return {"*build": True}


class DontBuildTemplate(TemplateAddon):
    """Template for io.StringIO object"""

    NAME = "dontbuild"

    @classmethod
    def data(self):
        return {"*build": False}


class CurrentWorkingDirectoryTemplate(TemplateAddon):

    NAME = "cwd"

    @classmethod
    def data(cls):
        return str(Path.cwd())


class SystemInfo(TemplateAddon):
    NAME = "systeminfo"

    @classmethod
    def data(cls):
        return {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_compiler": platform.python_compiler(),
            "node": platform.node(),
        }


class DateTimeNowTemplate(TemplateAddon):

    NAME = "datetimenow"

    @classmethod
    def data(cls):
        return str(datetime.datetime.now())


class UUID4Template(TemplateAddon):
    NAME = "uuid4"

    @classmethod
    def data(cls):
        """Returns a random version 4 UUID."""
        return str(uuid.uuid4())


def call_on(callable, *args, **kwargs):
    return callable(*args, **kwargs)


class CallTemplate(TemplateAddon):
    NAME = "call"

    @classmethod
    def data(cls):
        return {"*object": f"{cls.__module__}.call_on", "callable!required": None}


def include(file):
    if Path(file).suffix in FORMAT_READERS:
        return FORMAT_READERS[Path(file).suffix](file)
    else:
        raise IncludeModifierError(
            f"Unsupported file format {Path(a).suffix} for include modifier {a}"
        )

class IncludeTemplate(TemplateAddon):
    NAME = "include"

    @classmethod
    def data(cls):
        return {"*object": f"{cls.__module__}.include", "file!required": None}


