from dicfg.addons.addons import UpdaterAddon
from dicfg.config import Affix, ConfigDict, ConfigList, ConfigValue, update


class ReplaceUpdaterAddon(UpdaterAddon):

    NAME = "replace"

    @classmethod
    def update(cls, a: ConfigValue, b: ConfigValue):
        if isinstance(a, ConfigDict):
            return b.data
        return update(a, b)


class MergeUpdaterAddon(UpdaterAddon):

    NAME = "merge"

    @classmethod
    def update(cls, a: ConfigValue, b: ConfigValue):
        if isinstance(a, ConfigList):
            return a.data + b.data
        return update(a, b)


class PreUpdaterAddon(UpdaterAddon):

    NAME = "pre"

    @classmethod
    def update(cls, a: ConfigValue, b: ConfigValue):
        return update(a, b, affix=Affix.PRE)


class PostUpdaterAddon(UpdaterAddon):

    NAME = "post"

    @classmethod
    def update(cls, a: ConfigValue, b: ConfigValue):
        return update(a, b, affix=Affix.POST)
