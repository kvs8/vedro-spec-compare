import os
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

from .differ import Diff


class Generator:
    _PATH_TEMPLATES = os.path.dirname(os.path.realpath(__file__)) + '/templates'
    _TEMPLATE_COVERAGE = 'coverage.html.j2'

    def __init__(self) -> None:
        self._templates = Environment(loader=FileSystemLoader(self._PATH_TEMPLATES))

    def _get_template(self, template_name: str) -> Template:
        return self._templates.get_template(name=template_name)

    @staticmethod
    def _create_dir(dirname: str) -> None:
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    def _generate_by_template(self, file_path: str, template_name: str, **kwargs: Any) -> None:
        template = self._get_template(template_name=template_name)

        self._create_dir(os.path.dirname(file_path))
        with open(file_path, 'w') as file:
            file.write(template.render(**kwargs))

    def coverage_report(self, diff: Diff, file_path: str) -> None:
        self._generate_by_template(
            file_path=file_path,
            template_name=self._TEMPLATE_COVERAGE,
            **diff.data()
        )
