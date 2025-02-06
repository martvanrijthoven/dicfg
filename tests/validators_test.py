from pytest import raises
from dicfg.addons.addons import UnsupportedAddonError, ValidatorAddon
from dicfg.reader import ConfigReader
from dicfg.addons.validators import ValidationErrors


def test_succeed():
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    config_reader.read()


def test_required_error():
    user_config = {"validators": {"test2": ""}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_depreciated_error():
    user_config = {"validators": {"test": "hello"}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_key_error():
    user_config = {"validators": {"testing@updater(replace)": {"test": []}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_callable_error():
    user_config = {"validators": {"testing": {"*object": "io.StringIO2"}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_argument_error():
    user_config = {"validators": {"testing": {"initial_value2": "test"}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_no_dict_error():
    user_config = {"validators": {"testing@validator(object)@updater(replace)": []}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_no_callable_error():
    user_config = {"validators": {"testing@updater(replace)": {"*object": "datetime"}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_template():
    user_config = {"validators": {"testing2#debug": {"initial_value": "mart"}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    print(config_reader.read(user_config))


def test_template_same_type():
    user_config = {"validators": {"testing@template(debug)": {}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    config_reader.read(user_config)


def test_merge_config_value():
    user_config = {"validators": {"test_merge": 4}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    config_reader.read(user_config)


def test_replace_config_value():
    user_config = {"validators": {"testing2&replace": "test"}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    config_reader.read(user_config)


def test_duplicate_addonerror():
    _ = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValueError):

        class _(ValidatorAddon):
            """"""


def test_unsupported_addon():
    user_config = {"validators": {"testing2@uerror(replace)": "test"}}

    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(UnsupportedAddonError):
        config_reader.read(user_config)
