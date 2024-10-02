from typing import Any, Dict, List

import requests
import yaml
from schemax_openapi import SchemaData, collect_schema_data


class SpecMethod:
    def __init__(self, method: str, route: str, query_params: List[str], response_codes: List[str]):
        self.method = method
        self.route = route
        self.query_params = query_params
        self.response_codes = response_codes

    @staticmethod
    def create(data: Any) -> "SpecMethod":
        if isinstance(data, SchemaData):
            return SpecMethod(
                method=data.http_method,
                route=data.path,
                query_params=data.queries,
                response_codes=[str(data.status)]
            )
        else:
            raise ValueError("Unsupported data format")


class Parser:
    @classmethod
    def parse(cls, spec_path: str) -> Dict[str, SpecMethod]:
        if spec_path.startswith("http://") or spec_path.startswith("https://"):
            return cls.parse_from_url(spec_path)
        else:
            return cls.parse_from_file(spec_path)

    @staticmethod
    def parse_from_url(url: str) -> Dict[str, SpecMethod]:
        response = requests.get(url)
        content = yaml.safe_load(response.text)

        result = dict()
        for data in collect_schema_data(content):
            result[data.interface_method] = SpecMethod.create(data)
        return result

    @staticmethod
    def parse_from_file(file_path: str) -> Dict[str, SpecMethod]:
        with open(file_path) as f:
            content = yaml.safe_load(f)

        result = dict()
        for data in collect_schema_data(content):
            result[data.interface_method] = SpecMethod.create(data)

        return result
