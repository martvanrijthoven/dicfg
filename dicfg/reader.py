import ast
import json
import sys
from collections import defaultdict
from copy import deepcopy
from functools import partial, singledispatch
from pathlib import Path
from typing import List, Union

import yaml
from dicfg.config import merge


def _open_json_config(config_path):
    with open(str(config_path), encoding='utf8') as file:
        return json.load(file)


def _open_yaml_config(config_path):
    with open(str(config_path), encoding='utf8') as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


_FILE_READERS = {
    ".json": _open_json_config,
    ".yml": _open_yaml_config,
    ".yaml": _open_yaml_config,
}


class ConfigNotFoundError(Exception):
    """Raised when config file can not be found."""


class ConfigReader:
    """Reads config files"""

    NAME = "dicfg"
    DEFAULT_KEY = "default"
    CONFIG_FILE = "config.yml"

    _CONFIGS_FOLDER = None
    _PRESETS_FOLDER = None
    _CONFIG_PATH = None

    def __init_subclass__(cls) -> None:
        try:
            configuration_folder = Path(sys.modules[cls.__module__].__file__).parent
        except AttributeError:  # notebooks
            configuration_folder = Path()

        cls._CONFIGS_FOLDER = configuration_folder / "configs"
        cls._PRESETS_FOLDER = configuration_folder / "configs" / "presets"
        cls._CONFIG_PATH = cls._CONFIGS_FOLDER / cls.CONFIG_FILE

    @classmethod
    def read(
        cls,
        user_config: Union[dict, str, Path] = None,
        presets: tuple = (),
        context_keys=(),
        search_paths=(),
    ) -> dict:
        """Reads Config File

        Args:
            user_config (Union[dict, str, Path], optional): user_config Defaults to None.
            presets (tuple, optional): presets Defaults to ().
            context_keys (tuple, optional): context keys Defaults to ().
            search_paths (tuple, optional): search paths Defaults to ().

        Returns:
            dict: read configs
        """

        user_config_search_path = None
        if user_config is not None and not isinstance(user_config, dict):
            user_config_search_path = Path(user_config).parent

        search_paths = (
            Path(),
            user_config_search_path,
            cls._CONFIGS_FOLDER,
            cls._PRESETS_FOLDER,
            *search_paths,
        )

        cls_config = (
            cls._read(cls._CONFIG_PATH)
            if cls._CONFIG_PATH is not None and cls._CONFIG_PATH.exists()
            else {}
        )

        preset_configs = cls._read_presets(presets)
        user_config = cls._read_user_config(user_config)
        cli_config = cls._read_cli(sys.argv[1:])

        configs = (
            cls_config,
            *preset_configs,
            user_config,
            cli_config,
        )

        configs = cls._fuse_configs(configs, context_keys, search_paths)
        return merge(*configs).cast()

    @classmethod
    def _read(cls, config_path):
        config = _FILE_READERS[Path(config_path).suffix](config_path=config_path)
        return {} if config is None else config

    @classmethod
    def _read_presets(cls, presets):
        return tuple((cls._read(cls._PRESETS_FOLDER / preset) for preset in presets))

    @classmethod
    def _read_user_config(cls, user_config):
        if isinstance(user_config, dict):
            return user_config[cls.NAME]
        if user_config is None:
            return {}
        return cls._read_user_config(user_config[cls.NAME])

    @classmethod
    def _read_cli(cls, args: List[str]):
        dicts = []
        for arg in args:
            if "=" in arg:
                keys, value = arg.split("=")
                keys = keys.split(".")
                dicts.append(_create_dict_from_keys(keys, value))
        cli_config = merge(*dicts)
        return cli_config.get(cls.NAME, {})

    @classmethod
    def _fuse_configs(cls, configs, context_keys, search_paths):
        fuse_config = partial(
            cls._fuse_config, context_keys=context_keys, search_paths=search_paths
        )
        return tuple(map(fuse_config, configs))

    @classmethod
    def _fuse_config(cls, config: dict, context_keys: tuple, search_paths):
        config = _include_configs(config, search_paths)
        fused_config = deepcopy(
            {key: deepcopy(config.get("default", {})) for key in context_keys}
        )
        return merge(fused_config, config)


def _create_dict_from_keys(keys: list, value) -> dict:
    dictionary = defaultdict(dict)
    if len(keys) <= 1:
        dictionary[keys[0]] = ast.literal_eval(value)
    else:
        dictionary[keys[0]] = dict(_create_dict_from_keys(keys[1:], value))
    return dict(dictionary)


def _search_config(config_name: Union[str, Path], search_paths: tuple) -> Path:
    for search_path in search_paths:
        if search_path is None:
            continue
        config_path = Path(search_path) / config_name
        if config_path.exists():
            return config_path
    raise ConfigNotFoundError(config_name)


@singledispatch
def _include_configs(config, search_paths):
    return config


@_include_configs.register
def _include_configs_str(config: str, search_paths):
    if Path(config).suffix in _FILE_READERS:
        config_path = _search_config(config, search_paths)
        open_config = _FILE_READERS[Path(config_path).suffix](config_path)
        return _include_configs(open_config, search_paths)
    return config


@_include_configs.register
def _include_configs_dict(config: dict, search_paths):
    for key, value in config.items():
        config[key] = _include_configs(value, search_paths)
    return config
