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
    with open(str(config_path), encoding="utf8") as file:
        return json.load(file)


def _open_yaml_config(config_path):
    with open(str(config_path), encoding="utf8") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


_FILE_READERS = {
    ".json": _open_json_config,
    ".yml": _open_yaml_config,
    ".yaml": _open_yaml_config,
}


class ConfigNotFoundError(Exception):
    """Raised when config file can not be found."""


class ConfigReader:
    """ConfigReader

    Args:
        name (str): Name of config. Used as a reference in user configs and cli settings.
        main_config_path (Union[str, Path], optional): Path to main config. Defaults to  "./configs/config.yml".
        presets_folder_name (str, optional): Presets folder. Defaults to 'presets'.
        default_key (str, optional): Default context key. Defaults to "default".
        context_keys (tuple, optional): Addtional context keys. Defaults to ().
        search_paths (tuple, optional): Search paths for config file interpolation. Defaults to ().
    """

    def __init__(
        self,
        name: str,
        main_config_path: Union[str, Path] = "./configs/config.yml",
        presets_folder_name: str = "presets",
        default_key: str = "default",
        context_keys: tuple = (),
        search_paths: tuple = (),
    ):

        self._name = name
        self._main_config_path = Path(main_config_path)

        if not self._main_config_path.exists():
            raise ConfigNotFoundError(
                f"No main config file found at: {self._main_config_path}. The default main config path can be set via the 'main_config_path argument'"
            )

        self._default_key = default_key
        self._context_keys = context_keys
        self._search_paths = search_paths

        self._configs_folder = None
        self._presets_folder = None

        self._configs_folder = self._main_config_path.parent
        self._presets_folder = self._configs_folder / presets_folder_name

    def read(
        self,
        user_config: Union[dict, str, Path] = None,
        presets: tuple = (),
    ) -> dict:
        """Reads Config File

        Args:
            user_config (Union[dict, str, Path], optional): user_config Defaults to None.
            presets (tuple, optional): presets Defaults to ().

        Returns:
            dict: read configs
        """

        user_config_search_path = None
        if user_config is not None and not isinstance(user_config, dict):
            user_config_search_path = Path(user_config).parent

        search_paths = self._set_search_paths(
            user_config_search_path, self._search_paths
        )

        self_config = self._read(self._main_config_path)

        preset_configs = self._read_presets(presets)
        user_config = self._read_user_config(user_config)
        cli_config = self._read_cli(sys.argv[1:])

        configs = (self_config, *preset_configs, user_config, cli_config)
        configs = self._fuse_configs(configs, self._context_keys, search_paths)

        return merge(*configs).cast()

    def _set_search_paths(self, user_config_search_path, search_paths):
        return (
            Path(),
            user_config_search_path,
            self._configs_folder,
            self._presets_folder,
            *search_paths,
        )

    def _read(self, config_path):
        config = _FILE_READERS[Path(config_path).suffix](config_path=config_path)
        return {} if config is None else config

    def _read_presets(self, presets):
        return tuple((self._read(self._presets_folder / preset) for preset in presets))

    def _read_user_config(self, user_config):
        if isinstance(user_config, dict):
            return user_config[self._name]
        if user_config is None:
            return {}
        return self._read(user_config)[self._name]

    def _read_cli(self, args: List[str]):
        dicts = []
        for arg in args:
            if "=" in arg:
                keys, value = arg.split("=")
                keys = keys.split(".")
                dicts.append(_create_dict_from_keys(keys, value))
        cli_config = merge(*dicts)
        return cli_config.get(self._name, {})

    def _fuse_configs(self, configs, context_keys, search_paths):
        fuse_config = partial(
            self._fuse_config, context_keys=context_keys, search_paths=search_paths
        )
        return tuple(map(fuse_config, configs))

    def _fuse_config(self, config: dict, context_keys: tuple, search_paths):
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
