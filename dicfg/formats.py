import json
import yaml


def read_json_config(config_path):
    with open(str(config_path), encoding="utf8") as file:
        return json.load(file)


def read_yaml_config(config_path):
    with open(str(config_path), encoding="utf8") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


FORMAT_READERS = {
    ".json": read_json_config,
    ".yml": read_yaml_config,
    ".yaml": read_yaml_config,
}