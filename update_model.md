````markdown
# `init_model/update_model.py`

This script asks several LLMs to update an evaluation model (a JSON object describing grading criteria) based on a piece of textual feedback, lets the user pick the best response interactively, and saves every model's response to disk.

## What it does

1. Loads the API key from `secrets/api_key` (a single-line file at the repo root).
2. Loads the current evaluation model from `init_model/current_model.json`. If the file is missing or empty, it starts with `{}`.
3. Creates a timestamped run directory `init_model/temp/<YYYYMMDD_HHMMSS>/` for this invocation's outputs.
4. Picks which models to query. It pulls the list of available models from `config.model_map.ModelQuery` and keeps only those in the `ALLOWED_MODELS` set (`mistral-nemo`, `deepseek-v4-flash`, `qwen3.6-27b`).
5. For each allowed model, it:
   - Creates a `StatelessAgent` wrapping the OpenAI-compatible client pointed at `https://api.aitunnel.ru/v1/`.
   - Sends a prompt asking the model to extract criteria from the hard-coded `FEEDBACK` string and merge them into the current evaluation model. The prompt pins the output to the shape:
     ```json
     {"criteria": {"0": "<criterion 0 text>", "1": "<criterion 1 text>", ...}}
     ```
     where `criteria` is a JSON object with stringified zero-based indices as keys.
   - Writes the raw response to `init_model/temp/<YYYYMMDD_HHMMSS>/<model-name>.json` and keeps it as a candidate variant.
6. Handles non-reasoning unsupported errors. If the provider rejects the request because reasoning mode cannot be disabled for that model, the script writes a `.txt` placeholder noting the limitation instead of crashing (that model contributes no variant).
7. Prints all collected variants to the console (`--- Всего: X новых вариантов ---`, then `Вариант N (<model>): <JSON>` for each) and prompts the user to enter the number of the variant to use. The chosen JSON is parsed and written to `init_model/current_model.json` (falling back to a raw write if parsing fails). The full set of per-model responses stays in the timestamped `temp/` subfolder regardless of choice.

## Inputs

- `secrets/api_key` — API key for the aitunnel.ru gateway.
- `init_model/current_model.json` — the evaluation model to update.
- `config/model_map.json` — registry of available models (read via `ModelQuery`).
- `FEEDBACK` constant in the script — the natural-language feedback to incorporate.
- Console input — the number of the variant chosen by the user at the end of the run.

## Outputs

- `init_model/temp/<YYYYMMDD_HHMMSS>/<model>.json` — the updated evaluation model returned by each LLM for this run.
- `init_model/temp/<YYYYMMDD_HHMMSS>/<model>.txt` — written instead when the model doesn't support disabling reasoning.
- `init_model/current_model.json` — overwritten with the variant the user selected from the console.

## Running it

```bash
uv run python -m init_model.update_model
```
````