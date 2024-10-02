from pytest import raises
from dicfg.reader import ConfigReader
from dicfg.validators import UnsupportedValidatorError, ValidationErrors


def test_succeed():
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    config_reader.read()


def test_negative_number_error():
    user_config = {"validators": {"test": -2}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_empty_error():
    user_config = {"validators": {"test2": ""}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_negative_number_list_error():
    user_config = {"validators": {"test3": [-1]}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_negative_number_list_inner_error():
    user_config = {"validators": {"test4": {"test5": [-1]}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_key_error():
    user_config = {"validators": {"testing@replace(true)": {"test": []}}}
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
    user_config = {"validators": {"testing@validate(object)@replace(true)": []}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_object_no_callable_error():
    user_config = {"validators": {"testing@replace(true)": {"*object": "datetime"}}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(ValidationErrors):
        config_reader.read(user_config)


def test_invalid_validator_error():
    user_config = {"validators": {"testing@validate(error)@replace(true)": []}}
    config_reader = ConfigReader(
        name="validators",
        main_config_path="./configs/validators_config.yml",
    )
    with raises(UnsupportedValidatorError):
        config_reader.read(user_config)
