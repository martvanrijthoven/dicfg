from dicfg.configs.configvalue import ConfigValue


class ConfigSet(ConfigValue, set, data_type=set):
    def __new__(cls, data, updater=None, validator=None):
        processed = set(ConfigValue.factory(value) for value in data)
        return set.__new__(cls, processed)

    def _init(self, data: set):
        return set(ConfigValue.factory(value) for value in data)

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        return set(value.cast() for value in self.data)
