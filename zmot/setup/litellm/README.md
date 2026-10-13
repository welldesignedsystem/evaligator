# LiteLLM gateway (Docker) — OpenRouter to start

A local [LiteLLM](https://docs.litellm.ai/docs/proxy/docker_quick_start) proxy that exposes one
OpenAI-compatible endpoint (`http://localhost:4000`) over whatever models you configure, plus a
bundled Postgres so the Admin UI, virtual keys, and spend tracking work. Start on OpenRouter; add
direct providers or more models later without touching the code that calls it.

Everything here lives under `zmot/` (the experiment sandbox), so normal repo rules are relaxed.

## Why a gateway instead of calling OpenRouter directly

- One base URL + one key for your experiment code, regardless of provider.
- Model names are **logical** (`gpt-4o-mini`) and mapped to real providers in `config.yaml`.
  Swapping OpenRouter for a direct OpenAI/Anthropic/Gemini key later is a config edit.
- LiteLLM normalises responses and params, so the same client code works across providers.
- The Admin UI at `/ui` gives you model management, key generation, and spend logs.

## Prerequisites

- Docker with the Compose plugin (`docker --version`, `docker compose version`).
- An OpenRouter API key from <https://openrouter.ai/keys>.

## Setup

```bash
cd zmot/setup/litellm

# 1. Create your local env file and paste the OpenRouter key.
cp .env.example .env
$EDITOR .env

# 2. Start the proxy + Postgres.
docker compose up -d

# 3. Watch it come up (first boot runs DB migrations).
docker compose logs -f litellm
```

Generate long random values for `LITELLM_MASTER_KEY` and `LITELLM_SALT_KEY`:

```bash
printf 'sk-%s\n' "$(openssl rand -hex 32)"
```

## Admin UI

Open <http://localhost:4000/ui>.

- Username: `admin`
- Password: your `LITELLM_MASTER_KEY` value (unless you set `UI_USERNAME`/`UI_PASSWORD` in `.env`)

From the UI you can add models, mint virtual keys, and inspect spend. Note: the UI login is a
bootstrap/ shared **admin** credential — fine for a local sandbox, but for anything shared, create a
`proxy_admin` user and set `general_settings.disable_env_credential_login: true`.

## Verify the API (no UI needed)

```bash
export LITELLM_MASTER_KEY=sk-local-master-key   # match .env

# List the models the proxy knows about.
curl -s http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" | python -m json.tool

# Send a real completion (goes through OpenRouter).
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello in one word."}]
  }' | python -m json.tool
```

## Use it from experiment code

It speaks the OpenAI API, so any OpenAI-compatible client works:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:4000/v1", api_key="sk-local-master-key")
resp = client.chat.completions.create(
    model="gpt-4o-mini",                       # logical name from config.yaml
    messages=[{"role": "user", "content": "hi"}],
)
print(resp.choices[0].message.content)
```

## Using your proxy key from DeepEval

DeepEval ships a native `LiteLLMModel` that calls the `litellm` SDK, so point it at this proxy with
the `litellm_proxy/` prefix and the model's **logical name** from `config.yaml`.

Run a scratch script without touching `pyproject.toml` (nice for `zmot/`):

```bash
uv run --with deepeval --with litellm python zmot/your_script.py
```

```python
import os

from deepeval.metrics import AnswerRelevancyMetric
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase

judge = LiteLLMModel(
    model="litellm_proxy/gpt-4o-mini",          # logical name from config.yaml
    api_key=os.environ["LITELLM_API_KEY"],      # master key or a virtual key
    base_url="http://localhost:4000",           # note: no /v1 on this path
    temperature=0,
)

metric = AnswerRelevancyMetric(model=judge, threshold=0.5)
case = LLMTestCase(input="What is 2+2?", actual_output="4")
metric.measure(case)
print(metric.score, metric.reason)
```

Set the key in your shell or a `zmot/.env` (DeepEval autoloads `.env`):

```bash
export LITELLM_API_KEY=sk-local-master-key   # the LITELLM_MASTER_KEY from .env
```

DeepEval can also pick everything up from env instead of constructor args:

```dotenv
USE_LITELLM=1
LITELLM_MODEL_NAME=litellm_proxy/gpt-4o-mini
LITELLM_API_KEY=sk-local-master-key
LITELLM_API_BASE=http://localhost:4000
```

```bash
deepeval set-litellm --model=litellm_proxy/gpt-4o-mini --base-url=http://localhost:4000
# `deepeval set-litellm --help` for the API-key flag; otherwise LITELLM_API_KEY is read.
```

Prefer a plain OpenAI-compatible client instead? The proxy also speaks `/v1`, so any
OpenAI-SDK-based tool (including DeepEval's `OpenAIModel`) works with:

- base URL: `http://localhost:4000/v1`
- API key: the same LiteLLM key
- model: the logical name (`gpt-4o-mini`)

## Adding providers / models later

Edit `config.yaml`, add an entry, and restart:

```yaml
model_list:
  - model_name: gpt-4o-mini                      # existing OpenRouter route
    litellm_params:
      model: openrouter/openai/gpt-4o-mini
      api_key: os.environ/OPENROUTER_API_KEY

  - model_name: gpt-4o-mini-direct               # same logical model, direct provider
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY          # add this to .env
```

```bash
docker compose restart litellm
```

Provider string format is `provider/model` — e.g. `openai/...`, `anthropic/...`,
`google/...`, `openrouter/...`. Check current OpenRouter model slugs at
<https://openrouter.ai/models> and confirm the model string matches.

## Teardown

```bash
docker compose down          # stop; keeps the Postgres volume
docker compose down -v       # stop and wipe models/keys/spend data too
```

## Notes / gotchas

- `.env` here is gitignored (root `.gitignore`), `.env.example` is tracked.
- The port is bound to `127.0.0.1` on purpose — don't expose this proxy publicly.
- The proxy refuses to start without `LITELLM_MASTER_KEY` and `LITELLM_SALT_KEY`.
- Keep `LITELLM_SALT_KEY` stable: it encrypts DB-stored credentials. Changing it makes them
  unreadable (you'd re-enter keys).
- First `docker compose up` runs DB migrations; give it a few seconds before the UI responds.
