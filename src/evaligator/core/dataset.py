from __future__ import annotations

import json
import random
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from evaligator.core.errors import DatasetError
from evaligator.core.models import EvalCase


@dataclass
class Dataset:
    """An ordered, named collection of :class:`EvalCase` with load/save helpers."""

    name: str
    cases: list[EvalCase] = field(default_factory=list)

    @classmethod
    def from_json(cls, path: str) -> Dataset:
        source = Path(path)
        data = _read_json(source)
        if not isinstance(data, dict):
            raise DatasetError(f"{source}: dataset JSON must be an object")
        return cls(
            name=str(data.get("name", source.stem)), cases=_cases_from(data.get("cases", []))
        )

    @classmethod
    def from_jsonl(cls, path: str) -> Dataset:
        source = Path(path)
        text = _read_text(source)
        cases: list[EvalCase] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{source}:{lineno}: invalid JSON: {exc}") from exc
            cases.append(_case_from(record, where=f"{source}:{lineno}"))
        return cls(name=source.stem, cases=cases)

    def __len__(self) -> int:
        return len(self.cases)

    def __iter__(self) -> Iterator[EvalCase]:
        return iter(self.cases)

    def __getitem__(self, index: int) -> EvalCase:
        return self.cases[index]

    def filter_by_tag(self, tag: str) -> Dataset:
        return Dataset(name=self.name, cases=[case for case in self.cases if tag in case.tags])

    def sample(self, n: int, seed: int | None = None) -> Dataset:
        if not 0 <= n <= len(self.cases):
            raise ValueError(f"cannot sample {n} cases from a dataset of {len(self.cases)}")
        return Dataset(name=self.name, cases=random.Random(seed).sample(self.cases, n))

    def to_json(self, path: str | None = None) -> str:
        payload = {
            "name": self.name,
            "cases": [
                {
                    "input": case.input,
                    "expected": case.expected,
                    "metadata": dict(case.metadata),
                    "tags": list(case.tags),
                }
                for case in self.cases
            ],
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if path is not None:
            try:
                Path(path).write_text(text, encoding="utf-8")
            except OSError as exc:
                raise DatasetError(f"could not write dataset {path}: {exc}") from exc
        return text

    def stats(self) -> dict[str, Any]:
        tag_counts: dict[str, int] = {}
        for case in self.cases:
            for tag in case.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return {
            "name": self.name,
            "total": len(self.cases),
            "with_expected": sum(1 for case in self.cases if case.expected is not None),
            "tags": dict(sorted(tag_counts.items())),
        }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DatasetError(f"could not read dataset {path}: {exc}") from exc


def _read_json(path: Path) -> Any:
    text = _read_text(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DatasetError(f"{path}: invalid JSON: {exc}") from exc


def _cases_from(records: Any) -> list[EvalCase]:
    if not isinstance(records, list):
        raise DatasetError("dataset 'cases' must be a list")
    return [_case_from(record, where=f"case {index}") for index, record in enumerate(records)]


def _case_from(record: Any, *, where: str) -> EvalCase:
    if not isinstance(record, dict):
        raise DatasetError(f"{where}: each case must be a JSON object")
    if "input" not in record:
        raise DatasetError(f"{where}: missing required 'input'")
    return EvalCase(
        input=str(record["input"]),
        expected=record.get("expected"),
        metadata=dict(record.get("metadata", {})),
        tags=list(record.get("tags", [])),
    )
