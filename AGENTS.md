# AGENTS.md

## Repo status (verify before assuming anything)
- This repo now includes a minimal Python package scaffold, a project configuration, and a small test suite. The verified commands are:
  - Install dependencies: `. .venv/bin/activate && python -m pip install -e '.[dev]'`
  - Lint: `. .venv/bin/activate && python -m ruff check .`
  - Type check: `. .venv/bin/activate && python -m mypy evaligator`
  - Test: `. .venv/bin/activate && python -m pytest -q`
  - Single-test invocation: `. .venv/bin/activate && python -m pytest tests/test_core.py -q`
- Intended language is Python: the diagram and the package scaffold both follow Python dataclass-based types.
- `misc/class-diagram.mmd` remains a design reference; it is not a shipped API contract.

## Design reference: `misc/class-diagram.mmd`
- Mermaid class diagram of the intended architecture, grouped by colour: core types (`EvalCase`, `EvalResult`, `EvalReport`, `Dataset`, `ScoreResult`, `ScoreType`), a large `Scorer` hierarchy (exact/regex/JSON/syntax scorers, `LLMJudge` variants, RAG faithfulness scorers, agent-trajectory scorers, `CachedScorer`), guardrails, runners (`CostAwareRunner`, `TieredRunner`, `ConcurrentRunner`), dataset registry/versioning, regression + prompt registry, annotation, and production monitoring.
- Header caveat: members are annotations derived from a class reference in a book's `evals.md`; the evalkit source is not in this repo. Signatures are design intent, not existing APIs — never import or call them as if shipped code.
- Diagram inheritance for runners is conceptual (noted in-file): the book's code has them as standalone classes.

## Mermaid workflow (quirks are documented in the diagram header)
- Render: `npx -p @mermaid-js/mermaid-cli mmdc -i misc/class-diagram.mmd -o misc/class-diagram.png -b white --scale 16`
- Use `--scale 16`, not the default 8 — this diagram is twice as wide as the untyped one; scale 8 renders labels at half size.
- Dunder members must be written `+\_\_len\_\_()` in labels: mermaid pipes class labels through markdown, so plain `__len__` renders as bold `len` with underscores consumed.

## Maintenance
- Keep diagram-specific gotchas in the diagram header (they travel with the file); keep this file to facts that change how an agent works here.
- When toolchain files land (e.g. `pyproject.toml`), replace this file's "no commands" status with the verified lint -> typecheck -> test order and single-test invocation.
