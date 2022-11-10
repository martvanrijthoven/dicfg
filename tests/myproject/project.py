from dataclasses import dataclass


@dataclass
class ProjectComponent:
    name: str


class MyProject:
    def __init__(self, project_component: ProjectComponent):
        self._project_component = project_component

    def __str__(self) -> str:
        return f"Project Component name: {self._project_component.name}"
