from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaligator.core.dataset import Dataset
from evaligator.core.errors import DatasetError
from evaligator.core.models import EvalCase


def _case(
    text: str,
    expected: str | None = None,
    tags: tuple[str, ...] = (),
    metadata: dict[str, str] | None = None,
) -> EvalCase:
    return EvalCase(input=text, expected=expected, tags=list(tags), metadata=metadata or {})


def test_len_iter_and_indexing() -> None:
    cases = [_case("a"), _case("b")]
    dataset = Dataset(name="d", cases=cases)
    assert len(dataset) == 2
    assert list(dataset) == cases
    assert dataset[0] is cases[0]
    assert dataset[-1] is cases[1]


def test_filter_by_tag_returns_new_dataset_without_mutating_source() -> None:
    dataset = Dataset(
        name="d",
        cases=[_case("a", tags=("x",)), _case("b", tags=("y",)), _case("c", tags=("x",))],
    )
    filtered = dataset.filter_by_tag("x")
    assert [case.input for case in filtered] == ["a", "c"]
    assert filtered.name == "d"
    assert filtered is not dataset
    assert len(dataset) == 3


def test_sample_is_reproducible_with_a_seed() -> None:
    dataset = Dataset(name="d", cases=[_case(str(i)) for i in range(10)])
    first = dataset.sample(3, seed=42)
    second = dataset.sample(3, seed=42)
    assert len(first) == 3
    assert [case.input for case in first] == [case.input for case in second]
    assert len(dataset) == 10


def test_sample_rejects_counts_outside_the_dataset() -> None:
    dataset = Dataset(name="d", cases=[_case("a")])
    with pytest.raises(ValueError):
        dataset.sample(2)
    with pytest.raises(ValueError):
        dataset.sample(-1)


def test_to_json_returns_serialised_text() -> None:
    dataset = Dataset(name="geo", cases=[_case("capital?", "paris", tags=("geo",))])
    payload = json.loads(dataset.to_json())
    assert payload["name"] == "geo"
    assert payload["cases"] == [
        {"input": "capital?", "expected": "paris", "metadata": {}, "tags": ["geo"]}
    ]


def test_to_json_writes_file_when_path_given(tmp_path: Path) -> None:
    dataset = Dataset(name="geo", cases=[_case("q", "a")])
    path = tmp_path / "ds.json"
    text = dataset.to_json(str(path))
    assert path.read_text(encoding="utf-8") == text


def test_json_round_trip_preserves_name_and_cases(tmp_path: Path) -> None:
    original = Dataset(
        name="geo",
        cases=[_case("q", "a", tags=("t",), metadata={"k": "v"}), _case("q2")],
    )
    path = tmp_path / "ds.json"
    original.to_json(str(path))
    loaded = Dataset.from_json(str(path))
    assert loaded.name == original.name
    assert loaded.cases == original.cases


def test_from_json_missing_file_raises_dataset_error(tmp_path: Path) -> None:
    with pytest.raises(DatasetError):
        Dataset.from_json(str(tmp_path / "nope.json"))


def test_from_json_invalid_json_raises_dataset_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(DatasetError):
        Dataset.from_json(str(path))


def test_from_jsonl_reads_one_case_per_line(tmp_path: Path) -> None:
    path = tmp_path / "ms.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"input": "a", "expected": "b"}),
                json.dumps({"input": "c", "tags": ["x"]}),
                "",
            ]
        ),
        encoding="utf-8",
    )
    dataset = Dataset.from_jsonl(str(path))
    assert dataset.name == "ms"
    assert [case.input for case in dataset] == ["a", "c"]
    assert dataset[0].expected == "b"
    assert dataset[1].tags == ["x"]


def test_from_jsonl_bad_line_raises_dataset_error(tmp_path: Path) -> None:
    path = tmp_path / "ms.jsonl"
    path.write_text("not json\n", encoding="utf-8")
    with pytest.raises(DatasetError):
        Dataset.from_jsonl(str(path))


def test_stats_reports_counts_and_tag_distribution() -> None:
    dataset = Dataset(
        name="geo",
        cases=[
            _case("a", "x", tags=("geo", "easy")),
            _case("b", tags=("geo",)),
            _case("c"),
        ],
    )
    stats = dataset.stats()
    assert stats["name"] == "geo"
    assert stats["total"] == 3
    assert stats["with_expected"] == 1
    assert stats["tags"] == {"easy": 1, "geo": 2}
