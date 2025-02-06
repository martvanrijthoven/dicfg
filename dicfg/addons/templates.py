
from dicfg.addons.addon import TemplateAddon
from enum import Enum

class LogLevel(Enum):
    """Log level for templates"""
    DEBUG = "DEBUG"
    VERBOSE = "VERBOSE"


class Verbose(TemplateAddon):
    """Template"""

    NAME = "verbose"

    @classmethod
    def data(self):
        return {
            '*log': LogLevel.VERBOSE
        }


class Debug(TemplateAddon):
    """Template"""

    NAME = "debug"

    @classmethod
    def data(self):
        return {
            '*log': LogLevel.DEBUG
        }

class Build(TemplateAddon):
    """Template"""

    NAME = "build"

    @classmethod
    def data(self):
        return {
            '*build': True
        }

class DontBuild(TemplateAddon):
    """Template for io.StringIO object"""

    NAME = "dontbuild"

    @classmethod
    def data(self):
        return {
            '*build': False
        }
