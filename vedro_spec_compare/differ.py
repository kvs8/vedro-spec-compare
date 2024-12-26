from abc import abstractmethod
from typing import Any, Dict, List, Optional, Set

from .parser import SpecMethod


class DiffMethod:
    def __init__(self, method_data: SpecMethod, details: Optional[Dict[str, List[str]]] = None) -> None:
        self.http_method: str = method_data.method
        self.http_path: str = method_data.route
        self.details: Dict[str, List[str]] = details or {}


class Diff:
    def __init__(self) -> None:
        self.all: int = 0
        self.full: int = 0
        self.partial: int = 0
        self.empty: int = 0
        self.methods_full: List[DiffMethod] = []
        self.methods_partial: List[DiffMethod] = []
        self.methods_empty: List[DiffMethod] = []
        self.full_percent: float = 0
        self.partial_percent: float = 0
        self.empty_percent: float = 0
        self.stat_full_percent: float = 0
        self.stat_partial_percent: float = 0
        self.stat_empty_percent: float = 0

    def data(self) -> Dict[str, Any]:
        self.full_percent = round(self.full / self.all * 100, 2)
        self.partial_percent = 100 - self.full_percent - round(self.empty / self.all * 100, 2)
        self.empty_percent = 100 - self.full_percent - self.partial_percent

        stat_min_percent = 5
        self.stat_full_percent = (
            100
            - (max(self.empty_percent, stat_min_percent) if self.empty_percent else 0)
            - (max(self.partial_percent, stat_min_percent) if self.partial_percent else 0)
        )
        self.stat_partial_percent = (
            100
            - self.stat_full_percent
            - (max(self.empty_percent, stat_min_percent) if self.empty_percent else 0)
        )
        self.stat_empty_percent = 100 - self.stat_full_percent - self.stat_partial_percent

        return vars(self)

    def increase_all(self) -> None:
        self.all += 1

    def increase_full(self, method: SpecMethod) -> None:
        self.full += 1
        self.methods_full.append(DiffMethod(method))

    def increase_partial(self, method: SpecMethod, details: Dict[str, List[str]]) -> None:
        self.partial += 1
        self.methods_partial.append(DiffMethod(method, details))

    def increase_empty(self, method: SpecMethod) -> None:
        self.empty += 1
        self.methods_empty.append(DiffMethod(method))


class Differ:
    def __init__(self, golden_spec: Dict[str, SpecMethod], testing_spec: Dict[str, SpecMethod]) -> None:
        self.golden_spec = golden_spec
        self.testing_spec = testing_spec
        self.diff = Diff()

    @abstractmethod
    def get_diff(self) -> Diff:
        pass

    def diff_response_codes(self, method_id: str) -> Set[str]:
        return set(self.golden_spec[method_id].response_codes) - set(self.testing_spec[method_id].response_codes)

    def diff_queries(self, method_id: str) -> Set[str]:
        return set(self.golden_spec[method_id].query_params) - set(self.testing_spec[method_id].query_params)

    def diff_request_body_schema(self, method_id: str) -> List[str]:
        if (
            "properties" in self.golden_spec[method_id].body_request_schema
            and
            "properties" in self.testing_spec[method_id].body_request_schema
        ):
            return self.compare_schemas(
                self.golden_spec[method_id].body_request_schema["properties"],
                self.testing_spec[method_id].body_request_schema["properties"]
            )
        return []

    def diff_response_body_schema(self, method_id: str) -> List[str]:
        if (
            "properties" in self.golden_spec[method_id].response_schema
            and
            "properties" in self.testing_spec[method_id].response_schema
        ):
            return self.compare_schemas(
                self.golden_spec[method_id].response_schema["properties"],
                self.testing_spec[method_id].response_schema["properties"]
            )
        return []

    def compare_schemas(
            self, golden_schema: Dict[str, Any], testing_schema: Dict[str, Any], path: str = ""
    ) -> List[str]:
        differences = []

        for key in golden_schema:
            current_path = f"{path}.{key}" if path else key

            if key not in testing_schema:
                differences.append(current_path)

            elif golden_schema[key]["type"] == "array" and golden_schema[key]["items"]["type"] == "object":
                differences.extend(
                    self.compare_schemas(
                        golden_schema[key]["items"]["properties"],
                        testing_schema[key]["items"]["properties"],
                        current_path + ".[*]"
                    )
                )

            elif golden_schema[key]["type"] == 'object':
                differences.extend(
                    self.compare_schemas(
                        golden_schema[key]["properties"],
                        testing_schema[key]["properties"],
                        current_path
                    )
                )

        return differences


class DifferCoverage(Differ):
    def get_diff(self) -> Diff:
        for method_id in self.golden_spec.keys():
            self.diff.increase_all()

            if method_id not in self.testing_spec:
                self.diff.increase_empty(self.golden_spec[method_id])
                continue

            details = {}

            diff_codes = self.diff_response_codes(method_id)
            if diff_codes:
                details["Uncovered HTTP codes"] = list(diff_codes)

            diff_queries = self.diff_queries(method_id)
            if diff_queries:
                details["Uncovered query parameters"] = list(diff_queries)

            diff_request_body = self.diff_request_body_schema(method_id)
            if diff_request_body:
                details["Uncovered body request fields "] = diff_request_body

            diff_response_body = self.diff_response_body_schema(method_id)
            if diff_response_body:
                details["Uncovered body response fields "] = diff_response_body

            if details:
                self.diff.increase_partial(self.golden_spec[method_id], details)
                continue

            self.diff.increase_full(self.golden_spec[method_id])

        return self.diff


class DifferDiscrepancy(Differ):
    def get_diff(self) -> Diff:
        for method_id in self.golden_spec.keys():
            self.diff.increase_all()

            if method_id not in self.testing_spec:
                self.diff.increase_empty(self.golden_spec[method_id])
                continue

            details = {}

            diff_codes = self.diff_response_codes(method_id)
            if diff_codes:
                details["Undocumented HTTP codes"] = list(diff_codes)

            diff_queries = self.diff_queries(method_id)
            if diff_queries:
                details["Undocumented query parameters"] = list(diff_queries)

            diff_request_body = self.diff_request_body_schema(method_id)
            if diff_request_body:
                details["Undocumented body request fields "] = diff_request_body

            diff_response_body = self.diff_response_body_schema(method_id)
            if diff_response_body:
                details["Undocumented body response fields "] = diff_response_body

            if details:
                self.diff.increase_partial(self.golden_spec[method_id], details)
                continue

        return self.diff
