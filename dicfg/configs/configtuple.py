from dicfg.configs.configvalue import ConfigValue
from dicfg.configs.factory import create_config


class ConfigTuple(ConfigValue, tuple, data_type=tuple):
    def __new__(cls, data, updater=None, validator=None):
        config_values = tuple(create_config(value) for value in data)
        return tuple.__new__(cls, config_values)

    def _init(self, data: tuple):
        return tuple(create_config(value) for value in data)

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        return tuple(value.cast() for value in self.data)
