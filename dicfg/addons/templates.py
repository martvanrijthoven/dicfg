
from dicfg.addons.addons import TemplateAddon


class StringIOTemplate(TemplateAddon):
    """Validator that checks if a value is not empty or None"""

    NAME = "stringio"

    @property
    def data(self):
        return {
            "*object": "io.StringIO",
            "initial_value@validator(required)": "test",
            "newline": 3,
        }
