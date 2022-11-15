<img src="https://raw.githubusercontent.com/martvanrijthoven/dicfg/f6639bb5788b6426133967b1929e8f4374eab78a/docs/source/_static/logo.svg" width="50%" height="50%">


[![PyPI](https://img.shields.io/pypi/v/dicfg?color=0&label=pypi%20package)](https://pypi.org/project/dicfg/)
[![docs](https://github.com/martvanrijthoven/dicfg/actions/workflows/docs.yml/badge.svg)](https://github.com/martvanrijthoven/dicfg/actions/workflows/docs.yml)
[![tests](https://github.com/martvanrijthoven/dicfg/actions/workflows/tests.yml/badge.svg)](https://github.com/martvanrijthoven/dicfg/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/martvanrijthoven/dicfg/badge.svg?branch=main)](https://coveralls.io/github/martvanrijthoven/dicfg?branch=main)
[![codeinspector](https://api.codiga.io/project/34959/score/svg)](https://app.codiga.io/public/project/34959/dicfg/dashboard)
[![GitHub](https://img.shields.io/github/license/martvanrijthoven/dicfg)](https://github.com/martvanrijthoven/dicfg/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dicfg)
                  

Dicfg is a **configuration system** that supports **dependency injection** via **object interpolation** in config files.


## Installation

```bash
pip install dicfg
```
----


## Docs

[https://martvanrijthoven.github.io/dicfg/](https://martvanrijthoven.github.io/dicfg/)




Main Features

- Loading of predefined config files (YAML and JSON).
- Overwrite config with user_config files/dictionaries, command line interface, and/or presets.
- Customize merge/replace behavior for dictionaries and lists.
- Interpolation support for sub-config files, config variables, and environment variables.
- Build object instances directly in the config.
- Dependency injection via object interpolation: configure all object dependencies directly in the config.
- Use object attribute interpolation for referencing object attributes directly in the config file.


