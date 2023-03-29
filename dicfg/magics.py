import yaml
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring


@magics_class
class ConfigMagics(Magics):
    """
    IPython magic for loading YAML configuration files.
    """

    @classmethod
    def register_magics(cls):
        """
        Register the magics with IPython.
        """
        ip = get_ipython()
        ip.register_magics(cls)

    @cell_magic
    @magic_arguments()
    @argument("config", help="The name to give the loaded configuration object.")
    def yaml(self, args, content):
        """
        Load a YAML configuration file into a variable in the IPython namespace.
        """

        args = parse_argstring(self.yaml, args)
        try:
            config = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML: {exc}")
            return
        self.shell.user_ns[args.config] = config
