import sys
from dataclasses import dataclass
from pathlib import Path

from dicfg.factory import ObjectFactory
from dicfg.reader import ConfigNotFoundError, ConfigReader
from pytest import raises


@dataclass
class ProjectComponent:
    name: str


@dataclass
class MyProject:
    project_component: ProjectComponent


def test_my_project():
    sys.path.insert(0, str(Path(__file__).parent))
    config = ConfigReader.read("./testconfigs/myproject.yml")
    ObjectFactory.build(config["default"])


def test_dicfg():
    class TestConfigReader(ConfigReader):
        NAME = "testconfig"

    user_config_path = Path("./testconfigs/user_config.yml")
    config = TestConfigReader.read(
        user_config_path,
        fuse_keys=("testkey",),
        search_paths=(user_config_path.parent,),
    )
    test_config = ObjectFactory.build(
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

        user_config_path = Path("./testconfigs/user_config_not_found.yml")

        config = TestConfigReader.read(user_config_path, fuse_keys=("testkey",))

        ObjectFactory.build(config["testkey"])


def test_replace_error():
    with raises(ValueError):

        class TestConfigReader(ConfigReader):
            NAME = "testconfig"

        user_config_path = Path("./testconfigs/user_config_replace_error.yml")

        config = TestConfigReader.read(user_config_path, fuse_keys=("testkey",))

        ObjectFactory.build(config["testkey"])
