import sys
import os
from dataclasses import dataclass
from pathlib import Path

from pytest import raises

from dicfg import ConfigReader, build_config, __version__
from dicfg.reader import ConfigNotFoundError

os.environ["ENV_TEST_VAR"] = "dicfg"


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
    config = config_reader.read({"testconfig": {"default": None}})
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
    assert test_config["test_object_interpolation"] == __version__
    assert isinstance(test_config["test_object_list"][0], ConfigNotFoundError)
    assert test_config["test_object_reference"] is test_config["test_object"]


def test_cli():

    sys_config_reader = ConfigReader(
        name="testconfig",
        main_config_path="./configs/test.yml",
        context_keys=("testkey",),
    )
    sys_argv = sys.argv

    sys.argv = sys_argv + ["testconfig.default.test1.test2=10"]

    config = sys_config_reader.read()
    assert {"test1": {"test2": 10}} == config["default"]

    sys.argv = sys_argv + ["testconfig.default.test1.test2=10.0"]

    config = sys_config_reader.read()
    assert {"test1": {"test2": 10.0}} == config["default"]

    sys.argv = sys_argv + ["testconfig.default.test1.test2=True"]

    config = sys_config_reader.read()
    assert {"test1": {"test2": True}} == config["default"]

    sys.argv = sys_argv + ["testconfig.default.test1.test2=None"]

    config = sys_config_reader.read()
    assert {"test1": {"test2": None}} == config["default"]


def test_config_not_found_error():
    with raises(ConfigNotFoundError):

        user_config_path = Path("./testconfigs/user_config_not_found.yml")
        config = config_reader.read(user_config_path)
        build_config(config["testkey"])


def test_deep_replace():
    config_reader = ConfigReader(
        name="testconfig",
        main_config_path="./configs/config.yml",
    )
    config = config_reader.read(
        {"testconfig": {"default": {"deep_replace": {"c": 2}}}},
        presets=("deepreplace.yml",),
    )
    test_config = build_config(config["default"])
    assert test_config["deep_replace"] == {"c": 2, "d": 2}


def test_replace_error():
    with raises(ValueError):

        user_config_path = Path("./testconfigs/user_config_replace_error.yml")
        config = config_reader.read(user_config_path)
        build_config(config["testkey"])
