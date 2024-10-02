from typing import Any, Dict, List, Optional

from .parser import SpecMethod


class DiffMethod:
    def __init__(self, method_data: SpecMethod, details: Optional[List[str]] = None):
        self.http_method = method_data.method
        self.http_path = method_data.route
        self.details = details or []


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

    def increase_partial(self, method: SpecMethod, details: List[str]) -> None:
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

    def get_diff(self) -> Diff:
        for method_id in self.golden_spec.keys():
            self.diff.increase_all()

            if self.is_method_not_covered(method_id):
                continue

            if self.is_partial_method(method_id):
                continue

            self.diff.increase_full(self.golden_spec[method_id])

        return self.diff

    def is_method_not_covered(self, method_id: str) -> bool:
        if method_id not in self.testing_spec:
            self.diff.increase_empty(self.golden_spec[method_id])
            return True
        return False

    def is_partial_method(self, method_id: str) -> bool:
        details = []

        diff_codes = set(self.golden_spec[method_id].response_codes) - set(self.testing_spec[method_id].response_codes)
        if diff_codes:
            details.append(f"Not covered status codes: {','.join(diff_codes)}")

        diff_queries = set(self.golden_spec[method_id].query_params) - set(self.testing_spec[method_id].query_params)
        if diff_queries:
            details.append(f"Not covered params: {','.join(diff_queries)}")

        if details:
            self.diff.increase_partial(self.golden_spec[method_id], details)
            return True
        return False
