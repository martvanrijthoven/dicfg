from dataclasses import dataclass
from pathlib import Path

from dicfg.factory import build_config
from dicfg.reader import ConfigNotFoundError, ConfigReader
from pytest import raises, warns


@dataclass
class ProjectComponent:
    name: str


@dataclass
class MyProject:
    project_component: ProjectComponent


config_reader = ConfigReader(name="testconfig", context_keys=("testkey",))


def test_dicfg():
    user_config_path = Path("./testconfigs/user_config.yml")
    config = config_reader.read()
    config = config_reader.read({'testconfig': {'default': None}})
    config = config_reader.read(user_config_path)
    test_config = build_config(
        config["testkey"],
    )

    assert test_config["defaulttest"] == 10
    assert test_config["overridetest"] == 20
    assert test_config["test_dict"] == {"test2": "test2"}
    assert test_config["test_list_append"] == ["test", "test2"]
    assert test_config["test_list2"] == ["test", "test2"]
    assert test_config["test_list3"] == ["test2"]
    assert isinstance(test_config["test_object"], ConfigNotFoundError)
    assert test_config["test_object_type"] is ConfigNotFoundError
    assert isinstance(test_config["test_object_list"][0], ConfigNotFoundError)
    assert test_config["test_object_reference"] is test_config["test_object"]


def test_cli():

    config = config_reader._read_cli(["testconfig.test1.test2=10"]).cast()
    assert {"test1": {"test2": 10}} == config

    config = config_reader._read_cli(["testconfig.test1.test2=10.0"]).cast()
    assert {"test1": {"test2": 10.0}} == config

    config = config_reader._read_cli(["testconfig.test1.test2=True"]).cast()
    assert {"test1": {"test2": True}} == config

    config = config_reader._read_cli(["testconfig.test1.test2=None"]).cast()
    assert {"test1": {"test2": None}} == config


def test_config_not_found_error():
    with raises(ConfigNotFoundError):

        user_config_path = Path("./testconfigs/user_config_not_found.yml")
        config = config_reader.read(user_config_path)
        build_config(config["testkey"])


def test_replace_error():
    with raises(ValueError):

        user_config_path = Path("./testconfigs/user_config_replace_error.yml")
        config = config_reader.read(user_config_path)
        build_config(config["testkey"])

def test_warning():
    with warns(UserWarning):
        config_reader_empty = ConfigReader(name="testconfig", config_file_name='none').read()