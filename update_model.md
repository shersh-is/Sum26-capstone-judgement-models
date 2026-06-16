# `init_model/update_model.py`

This script asks several LLMs to update an evaluation model (a JSON object describing grading criteria) based on a piece of textual feedback, and saves each model's response to disk.

## What it does

1. Loads the API key from `secrets/api_key` (a single-line file at the repo root).
2. Loads the current evaluation model from `init_model/current_model.json`. If the file is missing or empty, it starts with `{}`.
3. Picks which models to query. It pulls the list of available models from `config.model_map.ModelQuery` and keeps only those in the `ALLOWED_MODELS` set (`mistral-nemo`, `deepseek-v4-flash`, `qwen3.6-27b`).
4. For each allowed model, it:
   - Creates a `StatelessAgent` wrapping the OpenAI-compatible client pointed at `https://api.aitunnel.ru/v1/`.
   - Sends a prompt asking the model to extract criteria from the hard-coded `FEEDBACK` string and merge them into the current evaluation model, returning a new JSON.
   - Writes the response to `init_model/temp/<model-name>.json`.
   The list of allowed models for now:
   - deepseek-v4-flash
   - qwen3.6-27b
5. Handles non-reasoning unsupported errors. If the provider rejects the request because reasoning mode cannot be disabled for that model, the script writes a `.txt` placeholder noting the limitation instead of crashing.

## Inputs

- `secrets/api_key` — API key for the aitunnel.ru gateway.
- `init_model/current_model.json` — the evaluation model to update.
- `config/model_map.json` — registry of available models (read via `ModelQuery`).
- `FEEDBACK` constant in the script — the natural-language feedback to incorporate.

## Outputs

- `init_model/temp/<model>.json` — the updated evaluation model returned by each LLM.
- `init_model/temp/<model>.txt` — written instead when the model doesn't support disabling reasoning.

## Running it

```bash
uv run python -m init_model.update_model
```
