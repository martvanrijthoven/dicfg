import argparse
from pathlib import Path
from tkinter import E


def config_py_content(name: str):
    return(
    f"from dicfg.reader import ConfigReader",
    f"from dicfg.factory import ObjectConfigFactory",
    f"",
    f"",
    f"class {name}ConfigReader(ConfigReader):",
    f"    NAME = \"{name.lower()}\"",
    f"",
    f"",
    f"class {name}ObjectConfigFactory(ObjectConfigFactory):",
    f"    CONFIG_READER = {name}ConfigReader",
    f""
    f"")


def main():
    parser = argparse.ArgumentParser(description='Setup configuration')
    parser.add_argument('--name', type=str, help='config name')

    args = parser.parse_args()

    (Path.cwd() / 'configs' / 'presets').mkdir(exist_ok=True, parents=True)
    (Path.cwd() / 'configs' / 'config.yml').touch()
    (Path.cwd() / 'config.py').touch()

    config_py = open(str((Path.cwd() / 'config.py')), 'w')
    config_py.write("\n".join(config_py_content(vars(args)['name'])))
    config_py.close()



if __name__ == "__main__":
    main()
