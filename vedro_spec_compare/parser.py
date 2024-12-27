from typing import Any, Dict, List

import requests
import yaml
from schemax_openapi import SchemaData, collect_schema_data


class SpecMethod:
    def __init__(
            self, method: str,
            route: str,
            query_params: List[str],
            request_body_schema: Dict[str, Any],
            response_codes: List[str],
            response_body_schema: Dict[str, Any]
    ):
        self.method = method
        self.route = route
        self.query_params = query_params
        self.body_request_schema = request_body_schema
        self.response_codes = response_codes
        self.response_schema = response_body_schema

    @staticmethod
    def create(data: Any) -> "SpecMethod":
        if isinstance(data, SchemaData):
            return SpecMethod(
                method=data.http_method,
                route=data.path,
                query_params=data.queries,
                request_body_schema=data.request_schema,
                response_codes=[str(data.status)],
                response_body_schema=data.response_schema
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

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data from {url}: status is {response.status_code}")

        content = yaml.load(response.text, Loader=yaml.CLoader)

        result = dict()
        for data in collect_schema_data(content):
            result[data.interface_method] = SpecMethod.create(data)
        return result

    @staticmethod
    def parse_from_file(file_path: str) -> Dict[str, SpecMethod]:
        try:
            with open(file_path) as f:
                content = yaml.load(f, Loader=yaml.CLoader)

            result = dict()
            for data in collect_schema_data(content):
                result[data.interface_method] = SpecMethod.create(data)

            return result

        except FileNotFoundError:
            raise ValueError(f"Failed to open file {file_path}: file not found")
