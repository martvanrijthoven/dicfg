from dicfg.configs.configvalue import ConfigValue


class ConfigTuple(ConfigValue, tuple, data_type=tuple):
    def __new__(cls, data, updater=None, validator=None):
        config_values = tuple(ConfigValue.factory(value) for value in data)
        return tuple.__new__(cls, config_values)

    def _init(self, data: tuple):
        return tuple(ConfigValue.factory(value) for value in data)

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        return tuple(value.cast() for value in self.data)
