from abc import abstractmethod
from typing import Any, Dict, List, Optional, Set

from .models import APIMethod, APIMethods


class MethodInfo:
    def __init__(self, method_data: APIMethod, diff_details: Optional[Dict[str, List[str]]] = None) -> None:
        self.http_method: str = method_data.method
        self.http_path: str = method_data.route
        self.diff_details: Dict[str, List[str]] = diff_details or {}


class Diff:
    def __init__(self) -> None:
        self.added: List[MethodInfo] = []
        self.similar: List[MethodInfo] = []
        self.modified: List[MethodInfo] = []
        self.missed: List[MethodInfo] = []

    def add_added(self, method: APIMethod) -> None:
        self.added.append(MethodInfo(method))

    def add_similar(self, method: APIMethod) -> None:
        self.similar.append(MethodInfo(method))

    def add_modified(self, method: APIMethod, diff_details: Dict[str, List[str]]) -> None:
        self.modified.append(MethodInfo(method, diff_details))

    def add_missed(self, method: APIMethod) -> None:
        self.missed.append(MethodInfo(method))


class Differ:
    def __init__(self, golden: APIMethods, testing: APIMethods) -> None:
        self.golden_ams = golden
        self.testing_ams = testing
        self.diff = Diff()

    @abstractmethod
    def get_diff(self) -> Any:
        pass

    def get_added_method_ids(self) -> Set[str]:
        return self.golden_ams.get_ids() - self.testing_ams.get_ids()

    def get_missed_method_ids(self) -> Set[str]:
        return self.testing_ams.get_ids() - self.golden_ams.get_ids()

    def get_common_method_ids(self) -> List[str]:
        return sorted(self.golden_ams.get_ids() & self.testing_ams.get_ids())

    def get_added_response_codes(self, method_id: str) -> Set[str]:
        return self.golden_ams[method_id].get_codes() - self.testing_ams[method_id].get_codes()

    def get_missed_response_codes(self, method_id: str) -> Set[str]:
        return self.testing_ams[method_id].get_codes() - self.golden_ams[method_id].get_codes()

    def get_common_response_codes(self, method_id: str) -> List[str]:
        return sorted(self.golden_ams[method_id].get_codes() & self.testing_ams[method_id].get_codes())

    def get_added_queries(self, method_id: str) -> Set[str]:
        return self.golden_ams[method_id].query_params - self.testing_ams.methods[method_id].query_params

    def get_missed_queries(self, method_id: str) -> Set[str]:
        return self.testing_ams[method_id].query_params - self.golden_ams[method_id].query_params

    def get_added_request_body_fields(self, method_id: str, content_type: str = "application/json") -> List[str]:
        return self.compare_schemas(
            self.golden_ams[method_id].request_body_schema[content_type].get("properties", {}),
            self.testing_ams[method_id].request_body_schema[content_type].get("properties", {})
        )

    def get_missed_request_body_fields(self, method_id: str, content_type: str = "application/json") -> List[str]:
        return self.compare_schemas(
            self.testing_ams.methods[method_id].request_body_schema[content_type].get("properties", {}),
            self.golden_ams.methods[method_id].request_body_schema[content_type].get("properties", {})
        )

    def get_added_response_body_fields(
            self, method_id: str, code: str, content_type: str = "application/json"
    ) -> List[str]:
        return self.compare_schemas(
            self.golden_ams[method_id].response_body_schema[code][content_type].get("properties", {}),
            self.testing_ams[method_id].response_body_schema[code][content_type].get("properties", {})
        )

    def get_missed_response_body_fields(
            self, method_id: str, code: str, content_type: str = "application/json"
    ) -> List[str]:
        return self.compare_schemas(
            self.testing_ams[method_id].response_body_schema[code][content_type].get("properties", {}),
            self.golden_ams[method_id].response_body_schema[code][content_type].get("properties", {})
        )

    def compare_schemas(
            self, golden_schema: Dict[str, Any], testing_schema: Dict[str, Any], path: str = ""
    ) -> List[str]:
        differences = []
        for key in golden_schema:
            current_path = f"{path}.{key}" if path else key
            if key not in testing_schema:
                differences.append(current_path)
            elif golden_schema[key]["type"] == "array" and golden_schema[key]["items"]["type"] == "object":
                differences.extend(self.compare_schemas(
                    golden_schema[key]["items"].get("properties", {}),
                    testing_schema[key]["items"].get("properties", {}),
                    current_path + ".[*]"
                ))
            elif golden_schema[key]["type"] == 'object':
                differences.extend(self.compare_schemas(
                    golden_schema[key].get("properties", {}),
                    testing_schema[key].get("properties", {}),
                    current_path
                ))
        return differences


class DiffDataCoverage:
    def __init__(self, diff: Diff):
        self.all: int = len(diff.added) + len(diff.similar) + len(diff.modified)
        self.full: int = len(diff.similar)
        self.partial: int = len(diff.modified)
        self.empty: int = len(diff.added)
        self.methods_full: List[MethodInfo] = diff.similar
        self.methods_partial: List[MethodInfo] = diff.modified
        self.methods_empty: List[MethodInfo] = diff.added
        self.full_percent: float = round(self.full / self.all * 100, 2)
        self.partial_percent: float = 100 - self.full_percent - round(self.empty / self.all * 100, 2)
        self.empty_percent: float = 100 - self.full_percent - self.partial_percent
        stat_min_percent = 5
        self.stat_full_percent: float = (
                100
                - (max(self.empty_percent, stat_min_percent) if self.empty_percent else 0)
                - (max(self.partial_percent, stat_min_percent) if self.partial_percent else 0)
        )
        self.stat_partial_percent: float = (
                100
                - self.stat_full_percent
                - (max(self.empty_percent, stat_min_percent) if self.empty_percent else 0)
        )
        self.stat_empty_percent: float = 100 - self.stat_full_percent - self.stat_partial_percent


class DifferCoverage(Differ):
    def get_diff(self) -> DiffDataCoverage:
        for method_id in self.get_added_method_ids():
            self.diff.add_added(self.golden_ams[method_id])

        for method_id in self.get_common_method_ids():
            details = {}

            added_queries = self.get_added_queries(method_id)
            if added_queries:
                details["Uncovered query parameters"] = list(added_queries)

            added_request_body_fields = self.get_added_request_body_fields(method_id)
            if added_request_body_fields:
                details["Uncovered request body fields"] = added_request_body_fields

            added_response_codes = self.get_added_response_codes(method_id)
            if added_response_codes:
                details["Uncovered response codes"] = list(added_response_codes)

            for code in self.get_common_response_codes(method_id):
                added_response_body_fields = self.get_added_response_body_fields(method_id, code)
                if added_response_body_fields:
                    details[f"Uncovered {code} response body fields"] = added_response_body_fields

            if details:
                self.diff.add_modified(self.golden_ams[method_id], details)
                continue

            self.diff.add_similar(self.golden_ams[method_id])

        return DiffDataCoverage(self.diff)


class DiffDataDiscrepancy:
    def __init__(self, diff: Diff):
        self.methods_partial: List[MethodInfo] = diff.modified
        self.methods_empty: List[MethodInfo] = diff.missed


class DifferDiscrepancy(Differ):
    def get_diff(self) -> DiffDataDiscrepancy:
        for method_id in self.get_missed_method_ids():
            self.diff.add_missed(self.testing_ams[method_id])

        for method_id in self.get_common_method_ids():
            details = {}

            missed_queries = self.get_missed_queries(method_id)
            if missed_queries:
                details["Undocumented query parameters"] = list(missed_queries)

            missed_request_body_fields = self.get_missed_request_body_fields(method_id)
            if missed_request_body_fields:
                details["Undocumented request body fields"] = missed_request_body_fields

            missed_response_codes = self.get_missed_response_codes(method_id)
            if missed_response_codes:
                details["Undocumented response codes"] = list(missed_response_codes)

            for code in self.get_common_response_codes(method_id):
                missed_response_body_fields = self.get_missed_response_body_fields(method_id, code)
                if missed_response_body_fields:
                    details[f"Undocumented {code} response body fields"] = missed_response_body_fields

            if details:
                self.diff.add_modified(self.golden_ams[method_id], details)
                continue

        return DiffDataDiscrepancy(self.diff)


class DiffDataChanges:
    def __init__(self, diff: Diff):
        self.added: List[MethodInfo] = diff.added
        self.modified: List[MethodInfo] = diff.modified
        self.deleted: List[MethodInfo] = diff.missed


class DifferChanges(Differ):
    def get_diff(self) -> DiffDataChanges:
        for method_id in self.get_added_method_ids():
            self.diff.add_added(self.golden_ams[method_id])

        for method_id in self.get_missed_method_ids():
            self.diff.add_missed(self.testing_ams[method_id])

        for method_id in self.get_common_method_ids():
            details = {}

            added_queries = self.get_added_queries(method_id)
            if added_queries:
                details["New query parameters"] = list(added_queries)

            missed_queries = self.get_missed_queries(method_id)
            if missed_queries:
                details["Deleted query parameters"] = list(missed_queries)

            added_request_body_fields = self.get_added_request_body_fields(method_id)
            if added_request_body_fields:
                details["New request body fields"] = added_request_body_fields

            missed_request_body_fields = self.get_missed_request_body_fields(method_id)
            if missed_request_body_fields:
                details["Deleted request body fields"] = missed_request_body_fields

            added_response_codes = self.get_added_response_codes(method_id)
            if added_response_codes:
                details["New response codes"] = list(added_response_codes)

            missed_response_codes = self.get_missed_response_codes(method_id)
            if missed_response_codes:
                details["Deleted response codes"] = list(missed_response_codes)

            for code in self.get_common_response_codes(method_id):
                added_response_body_fields = self.get_added_response_body_fields(method_id, code)
                if added_response_body_fields:
                    details[f"New {code} response body fields"] = added_response_body_fields

                missed_response_body_fields = self.get_missed_response_body_fields(method_id, code)
                if missed_response_body_fields:
                    details[f"Deleted {code} response body fields"] = missed_response_body_fields

            if details:
                self.diff.add_modified(self.golden_ams[method_id], details)
                continue

        return DiffDataChanges(self.diff)
