from config.model_map import ModelQuery
import json
import os

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


os.makedirs(OUTPUT_DIR, exist_ok=True)
current_model = load_current_model()

ALLOWED_MODELS = {"mistral-nemo", "deepseek-v4-flash", "qwen3.6-27b"}

models = [name for name in ModelQuery().names() if name in ALLOWED_MODELS]
for model in models:
    agent = StatelessAgent(
        model,
        "Respond very concisely (one sentence only) and to the point without complex formatting.",
    )
    try:
        text, response = agent.query(
            f"Given the feedback {FEEDBACK} and current state of evaluation model "
            f"{current_model}, extract criteria from the feedback and update the "
            f"model. Evaluation model can contain more than 1 criteria. Split "
            f"different criteria into different fields in JSON. Return just the "
            f"new JSON evaluation model"
        )
        out_path = os.path.join(OUTPUT_DIR, f"{safe_filename(model)}.json")
        with open(out_path, "w") as file:
            file.write(text)
    except Exception as e:
        if "is mandatory" in str(e) or "cannot be disabled" in str(e):
            out_path = os.path.join(OUTPUT_DIR, f"{safe_filename(model)}.txt")
            with open(out_path, "w") as file:
                file.write("Non-reasoning mode is not supported!")
        else:
            raise
