from dicfg.addons.addons import UpdaterAddon
from dicfg.config import ConfigDict, ConfigList, ConfigValue, update


class ReplaceUpdaterAddon(UpdaterAddon):

    NAME = "replace"

    def update(self, a: ConfigValue, b: ConfigValue):
        if isinstance(a, ConfigDict):
            return b.data
        return update(a, b)
       

class MergeUpdaterAddon(UpdaterAddon):

    NAME = "merge"

    def update(self, a: ConfigValue, b: ConfigValue):
        if isinstance(a, ConfigList):
            return a.data + b.data
        return update(a, b)