# AGENTS.md

## Repo status
- `uv`-managed Python project (`src/` layout, `py.typed`). `.python-version` = 3.14, `requires-python = ">=3.14"`, build backend `uv_build`. Use `uv`, never pip/venv.
- Verified commands (run in this order before finishing):
  - Sync deps: `uv sync --group dev`
  - Format: `uv run ruff format .`
  - Lint: `uv run ruff check .`
  - Type check: `uv run mypy` (strict; `files = ["src", "tests"]`)
  - Layering: `uv run lint-imports`
  - Test: `uv run pytest` — single test: `uv run pytest tests/unit/scorers/test_exact.py -q`
  - CLI: `uv run evaligator` (entrypoint `evaligator:main`)
- Config for all of the above lives in `pyproject.toml` (`[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.importlinter]`).

## ZMOT scratch area (`zmot/`)
- `zmot/` is a sandbox for experiments ("zero moment of truth"). Throwaway code lives there.
- Relaxed rules inside `zmot/`: no requirement to run format/lint/mypy/lint-imports, no contract suite, no ports-and-adapters layering, no public-API re-export. Skip `zmot/` when running the verification pipeline; keep `src/` and `tests/` strict.
- Nothing in `zmot/` is importable by `src/` — it is a leaf, never a dependency.

## Architecture rules (enforced, not aspirational)
- Ports & adapters. Dependency direction is one-way: `core` imports only the stdlib; domain packages (`scorers`, later `runners`/`datasets`/…) depend on `core`; **third-party eval SDKs are imported only under `integrations/`** (not built yet).
- `uv run lint-imports` enforces the `domain layering` contract. Extend its `layers` list in `pyproject.toml` as new packages land — a new package not listed is not checked.
- Third-party eval frameworks (deepeval, braintrust, langfuse; promptfoo is a Node CLI, adapter shells out) are **optional extras**, never core dependencies. Core must install and test with zero third-party SDKs.
- The public API is a curated re-export list in `src/evaligator/__init__.py`; keep it deliberate.

## TDD conventions
- Tests mirror `src/` paths under `tests/unit/` and `tests/integration/`.
- `tests/contract/` holds behavioural contract suites every implementation must satisfy. Subclass `ScorerContract` (`tests/contract/scorer_contract.py`), provide the `scorers` and `samples` fixtures, and name the subclass `Test...`. **Every new `Scorer` (built-in or adapter) must pass the contract suite.**
- Test packages use `__init__.py` files (needed so mypy and pytest agree on module names). Pytest config sets `pythonpath = ["."]`, so import shared helpers as `tests.contract.scorer_contract`.
- Build in vertical slices (core model → contract test → first implementation), not broad empty scaffolds.

## Design reference: `misc/class-diagram.mmd`
- Mermaid class diagram of the intended architecture, grouped by colour: core types (`EvalCase`, `EvalResult`, `EvalReport`, `Dataset`, `ScoreResult`, `ScoreType`), a large `Scorer` hierarchy (exact/regex/JSON/syntax scorers, `LLMJudge` variants, RAG faithfulness scorers, agent-trajectory scorers, `CachedScorer`), guardrails, runners (`CostAwareRunner`, `TieredRunner`, `ConcurrentRunner`), dataset registry/versioning, regression + prompt registry, annotation, and production monitoring.
- Header caveat: members are annotations derived from a class reference in a book's `evals.md`; the evalkit source is not in this repo. Signatures are design intent, not existing APIs — never import or call them as if shipped code.
- Diagram inheritance for runners is conceptual (noted in-file): the book's code has them as standalone classes.
- Read the file header before editing: it documents per-class notes and conventions (Scorer subclasses override name/score_type/threshold so those overrides are not repeated; `Scorer.score()` also accepts `**kwargs`; book properties are drawn as attributes).

## Mermaid workflow
- Render: `npx -p @mermaid-js/mermaid-cli mmdc -i misc/class-diagram.mmd -o misc/class-diagram.png -b white --scale 16`
- Use `--scale 16`, not the default 8 — this diagram is twice as wide as the untyped one. These quirks are duplicated in the diagram header (they travel with the file); keep AGENTS.md to facts that change how an agent works here.
- Dunder members must be written `+\_\_len\_\_()` in labels: mermaid pipes class labels through markdown, so plain `__len__` renders as bold `len` with underscores consumed.
