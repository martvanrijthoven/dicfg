from dicfg.addons.addon import UpdaterAddon
from dicfg.configs.configdict import ConfigDict
from dicfg.configs.configlist import ConfigList
from dicfg.configs.configset import ConfigSet
from dicfg.configs.configtuple import ConfigTuple
from dicfg.configs.configvalue import Affix, ConfigValue, update


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
        if isinstance(a, (ConfigList, ConfigTuple)):
            return a.data + b.data
        if isinstance(a, ConfigSet):
            return a.data.union(b.data)

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


class NonEmptyUpdater(UpdaterAddon):

    NAME = "~"

    @classmethod
    def update(cls, a: ConfigValue, b: ConfigValue):
        return a
