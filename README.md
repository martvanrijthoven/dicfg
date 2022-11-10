# dicfg

[![PyPI version](https://badge.fury.io/py/dicfg.svg)](https://badge.fury.io/py/dicfg)
[![tests](https://github.com/martvanrijthoven/dicfg/actions/workflows/tests.yml/badge.svg)](https://github.com/martvanrijthoven/dicfg/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/martvanrijthoven/dicfg/badge.svg?branch=main)](https://coveralls.io/github/martvanrijthoven/dicfg?branch=main)
[![codeinspector](https://api.codiga.io/project/34959/score/svg)](https://app.codiga.io/public/project/34959/dicfg/dashboard)

                  

A configuration system supporting direct dependency injection in config files.

## Installation

```bash
pip install dicfg
```
----


## Basic Example 


#### Project Code

```python 
from dataclasses import dataclass


@dataclass
class ProjectComponent:
    name: str 


@dataclass
class MyProject:
    project_component: ProjectComponent
```


#### User Config
```yaml 
dicfg:
  default:

    project_component:
      module: myproject.project
      attribute: ProjectComponent
      name: my_project_component

    project:
      module: myproject.project
      attribute: MyProject
      project_component: ${project_component}
```

#### Application Code

```python 
from dicfg.reader import ConfigReader
from dicfg.factory import ObjectConfigFactory
from myproject.project import MyProject


def main():
    project_config = ConfigReader.read("./user_config.yml")
    project_build = ObjectConfigFactory.build(project_config["default"])
    assert isinstance(project_build['project'], MyProject)

if __name__ == "__main__":
    main()
```

<!-- end basic-example -->

----

## Documentation

 - Setting up your project
 - Config inputs
   - config.py
   - presets
   - user_config
   - command line interface
 - ConfigReader options
   - user_config
   - presets
   - fuse_keys
   - search paths
 - Config dialect
   - objects
     - module
     - attribute
     - kwargs
   - :return_type 
   - ${references}
   - @replace
   
