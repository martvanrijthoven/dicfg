from dicfg.configs.configvalue import ConfigValue
from dicfg.configs.factory import create_config


class ConfigSet(ConfigValue, set, data_type=set):
    def __new__(cls, data, updater=None, validator=None):
        processed = set(create_config(value) for value in data)
        return set.__new__(cls, processed)

    def _init(self, data: set):
        return set(create_config(value) for value in data)

    def validate(self):
        yield from super().validate()
        for value in self.data:
            yield from value.validate()

    def cast(self):
        return set(value.cast() for value in self.data)
