import ast
import sys
from collections import defaultdict
from copy import deepcopy
from functools import partial, singledispatch
from pathlib import Path
from typing import List, Optional, Union
from dicfg.config import merge
from dicfg.addons.validators import ValidationErrors
from dicfg.addons import load as _
from dicfg.formats import FORMAT_READERS
from pprint import pprint

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
        presets: Union[str, Path] = "presets",
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

        if isinstance(presets, Path):
            self._presets_folder = presets
        else:
            self._presets_folder = self._configs_folder / presets

    def read(
        self,
        user_config: Optional[Union[dict, str, Path, list[dict, str, Path]]] = None,
        presets: tuple = (),
    ) -> dict:
        """Reads Config File

        Args:
            user_config (Union[dict, str, Path], optional): user_config Defaults to None.
            presets (tuple, optional): presets Defaults to ().

        Returns:
            dict: read configs
        """

        self_config = self._read(self._main_config_path)
        arg_preset_configs = self._read_presets(presets)
        cli_config = self._read_cli(sys.argv[1:])

        user_configs = []
        user_presets_configs = []
        user_config_search_paths = []
        if user_config is not None:
            if not isinstance(user_config, (list, tuple)):
                user_config = [user_config]

            for config in user_config:
                if isinstance(config, (str, Path)) and not isinstance(config, dict):
                    user_config_search_path = Path(config).parent
                    user_config_search_paths.append(user_config_search_path)
                read_user_config = self._read_user_config(config)
                user_presets = read_user_config.pop("presets", ())
                user_configs.append(read_user_config)
                user_presets_configs.extend(self._read_presets(user_presets))

        configs = (
            self_config,
            *tuple(user_presets_configs),
            *tuple(arg_preset_configs),
            *tuple(user_configs),
            cli_config,
        )

        search_paths = self._set_search_paths(
            user_config_search_paths, self._search_paths
        )

        configs = self._fuse_configs(configs, self._context_keys, search_paths)
        pprint(configs)
        merged_configs = merge(*configs)
        
        if errors := list(merged_configs.validate()):
            raise ValidationErrors(errors)
        return merged_configs.cast()

    def _set_search_paths(self, user_config_search_paths, search_paths):
        return (
            Path(),
            *tuple(user_config_search_paths),
            self._configs_folder,
            self._presets_folder,
            *search_paths,
        )

    def _read(self, config_path):
        config = FORMAT_READERS[Path(config_path).suffix](config_path=config_path)
        return {} if config is None else config

    def _read_presets(self, presets):
        return tuple((self._read(self._presets_folder / preset) for preset in presets))

    def _read_user_config(self, user_config):
        user_config = (
            user_config if isinstance(user_config, dict) else self._read(user_config)
        )

        try:
            return user_config[self._name]
        except KeyError:
            raise KeyError(
                f"Config file: {user_config} does not contain a '{self._name}' key."
            )

    def _read_cli(self, args: List[str]):
        dicts = []
        for arg in args:
            if arg.startswith(self._name) and "=" in arg:
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
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            value = ast.literal_eval("'" + value + "'")
        dictionary[keys[0]] = value
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
    if Path(config).suffix in FORMAT_READERS:
        config_path = _search_config(config, search_paths)
        open_config = FORMAT_READERS[Path(config_path).suffix](config_path)
        return _include_configs(open_config, search_paths)
    return config


@_include_configs.register
def _include_configs_dict(config: dict, search_paths):
    for key, value in config.items():
        config[key] = _include_configs(value, search_paths)
    return config
