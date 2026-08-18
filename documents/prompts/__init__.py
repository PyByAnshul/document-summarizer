from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(filename):
    prompt_path = PROMPTS_DIR / filename

    return prompt_path.read_text(
        encoding="utf-8"
    )