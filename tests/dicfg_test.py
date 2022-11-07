from pathlib import Path

from dicfg.factory import ObjectConfigFactory
from dicfg.reader import ConfigReader, ConfigNotFoundError
from pytest import raises
import sys

from dataclasses import dataclass


@dataclass
class ProjectComponent:
    name: str 

@dataclass
class MyProject:
    project_component: ProjectComponent


def test_my_project():
    sys.path.insert(0, str(Path(__file__).parent))
    config = ConfigReader.read('./testconfigs/myproject.yml')
    ObjectConfigFactory.build(config['default'])

def test_dicfg():
    class TestConfigReader(ConfigReader):
        NAME = "testconfig"

    class TestConfigFactory(ObjectConfigFactory):
        CONFIG_READER = TestConfigReader

    user_config_path = Path("./testconfigs/user_config.yml")
    config = TestConfigReader.read(
        user_config_path,
        fuse_keys=("testkey",),
        search_paths=(user_config_path.parent,),
    )
    test_config = TestConfigFactory.build(
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
    name = test_config["test_object_from_file"].__class__.__name__
    assert name == "ConfigNotFoundError"
    assert test_config["test_object_reference"] is test_config["test_object"]
    assert test_config["test_object_reference_using_name"] == "ConfigNotFoundError"


def test_cli():
    class TestConfigReader(ConfigReader):
        NAME = "testconfig"

    config = TestConfigReader()._read_cli(["testconfig.test1.test2=10"]).cast()
    assert {"test1": {"test2": 10}} == config

    config = TestConfigReader()._read_cli(["testconfig.test1.test2=10.0"]).cast()
    assert {"test1": {"test2": 10.0}} == config

    config = TestConfigReader()._read_cli(["testconfig.test1.test2=True"]).cast()
    assert {"test1": {"test2": True}} == config

    config = TestConfigReader()._read_cli(["testconfig.test1.test2=None"]).cast()
    assert {"test1": {"test2": None}} == config


def test_config_not_found_error():
    with raises(ConfigNotFoundError):

        class TestConfigReader(ConfigReader):
            NAME = "testconfig"

        class TestConfigFactory(ObjectConfigFactory):
            CONFIG_READER = TestConfigReader

        user_config_path = Path("./testconfigs/user_config_not_found.yml")

        config = TestConfigReader.read(user_config_path, fuse_keys=("testkey",))

        TestConfigFactory.build(
            config["testkey"]
        )


def test_replace_error():
    with raises(ValueError):

        class TestConfigReader(ConfigReader):
            NAME = "testconfig"

        class TestConfigFactory(ObjectConfigFactory):
            CONFIG_READER = TestConfigReader

        user_config_path = Path("./testconfigs/user_config_replace_error.yml")

        config = TestConfigReader.read(user_config_path, fuse_keys=("testkey",))

        TestConfigFactory.build(
            config["testkey"]
        )

