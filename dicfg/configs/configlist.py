from collections import UserList

from dicfg.configs.configvalue import ConfigValue
from dicfg.configs.factory import create_config


class ConfigList(ConfigValue, UserList, data_type=list):
    """Wraps a value into a ConfigList

    Args:
        data (list): value of the config

    """

    def _init(self, data: list):
        for idx, value in enumerate(data):
            data[idx] = create_config(value)
        return data

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        """Cast wrapped value to builtin python value"""
        return [value.cast() for value in self.data]