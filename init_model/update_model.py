from config.model_map import ModelQuery
import json
import os
from datetime import datetime

from openai import OpenAI


PROVIDER_BASE_URL = "https://api.aitunnel.ru/v1/"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
API_KEY_PATH = os.path.join(REPO_ROOT, "secrets", "api_key")
CURRENT_MODEL_PATH = os.path.join(HERE, "current_model.json")
OUTPUT_DIR = os.path.join(HERE, "temp")

FEEDBACK = (
    "The housing price dataset was not explicitly loaded from a CSV file into a "
    "pandas DataFrame, the absence of missing values after handling was not "
    "explicitly verified, and the number or proportion of price outliers was not "
    "explicitly displayed."
)


class StatelessAgent:
    def __init__(self, model: str, instructions: str):
        with open(API_KEY_PATH) as file:
            self.api_key = file.read().strip()

        self.model = model
        self.instructions = instructions
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=PROVIDER_BASE_URL,
        )

    def query(self, message: str):
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=message,
            max_output_tokens=10000,
            top_logprobs=3,
            extra_body={
                "reasoning": {
                    "enabled": False
                }
            },
        )

        return response.output_text, response


def load_current_model() -> str:
    if not os.path.exists(CURRENT_MODEL_PATH) or os.path.getsize(CURRENT_MODEL_PATH) == 0:
        return "{}"
    with open(CURRENT_MODEL_PATH) as file:
        return file.read().strip() or "{}"


def safe_filename(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


processed_dttm = datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = os.path.join(OUTPUT_DIR, processed_dttm)
os.makedirs(run_dir, exist_ok=True)

current_model = load_current_model()

ALLOWED_MODELS = {"mistral-nemo", "deepseek-v4-flash", "qwen3.6-27b"}

models = [name for name in ModelQuery().names() if name in ALLOWED_MODELS]

variants = []  # list of (model_name, text)

for model in models:
    agent = StatelessAgent(
        model,
        "Respond only with raw JSON (no markdown, no commentary).",
    )
    try:
        text, response = agent.query(
            f"Given the feedback {FEEDBACK} and the current evaluation model "
            f"{current_model}, extract criteria from the feedback and update the "
            f"model. Return a single JSON object with EXACTLY this top-level "
            f"shape: {{\"criteria\": {{\"0\": \"<criterion 0 text>\", \"1\": "
            f"\"<criterion 1 text>\", ...}}}}. The value of \"criteria\" must be "
            f"a JSON object whose keys are stringified zero-based indices (\"0\", "
            f"\"1\", \"2\", ...) and whose values are the criterion descriptions "
            f"as strings. Do not include any other top-level fields. Return only "
            f"the JSON, with no surrounding text or code fences."
        )
        out_path = os.path.join(run_dir, f"{safe_filename(model)}.json")
        with open(out_path, "w") as file:
            file.write(text)
        variants.append((model, text))
    except Exception as e:
        if "is mandatory" in str(e) or "cannot be disabled" in str(e):
            out_path = os.path.join(run_dir, f"{safe_filename(model)}.txt")
            with open(out_path, "w") as file:
                file.write("Non-reasoning mode is not supported!")
        else:
            raise


if not variants:
    print("Нет вариантов для выбора — ни одна модель не вернула результат.")
else:
    print(f"\n--- Всего: {len(variants)} новых вариантов ---")
    for idx, (model, text) in enumerate(variants, start=1):
        print(f"\nВариант {idx} ({model}):")
        print(text)

    prompt = (
        f"\nВведите в консоль номер варианта (1-{len(variants)}), "
        f"который выбрать для обновления current_model.json: "
    )
    while True:
        choice = input(prompt).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(variants):
            chosen_idx = int(choice) - 1
            break
        print(f"Введите число от 1 до {len(variants)}.")

    chosen_model, chosen_text = variants[chosen_idx]
    try:
        parsed = json.loads(chosen_text)
        with open(CURRENT_MODEL_PATH, "w") as file:
            json.dump(parsed, file, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        with open(CURRENT_MODEL_PATH, "w") as file:
            file.write(chosen_text)
    print(f"current_model.json обновлён вариантом {chosen_idx + 1} ({chosen_model}).")
