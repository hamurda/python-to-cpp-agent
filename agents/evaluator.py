import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_MESSAGE = (
    "You are a C++ code reviewer. Your job is to evaluate whether a C++ translation "
    "of Python code computes the same results, without executing it. "
    "You will be given the original Python code, the C++ translation, and test cases. "
    "Focus on COMPUTATIONAL CORRECTNESS: does the C++ implement the same algorithm "
    "and produce the same numerical results? "
    "Check for: logical equivalence, integer overflow risks, and missing headers. "
    "DO NOT fail the translation for: output formatting differences (print prefixes, "
    "decimal precision, spacing), exception message wording, or minor stylistic differences "
    "that don't affect the computed result. "
    "If the core computation is correct but formatting differs, verdict should be PASS "
    "and you can note the formatting differences as non-blocking observations. "
    "Respond only in valid JSON — no preamble, no markdown fences. "
    "Format: {\"verdict\": \"PASS\" | \"FAIL\" | \"WARN\", \"confidence\": int (0-100), "
    "\"issues\": [str], \"summary\": str}"
)


class Evaluator:
    def __init__(self, model: str = "gpt-5-mini"):
        self.client = OpenAI()
        self.model = model

    def run(self, python_code: str, cpp_code: str, test_cases: dict) -> dict:
        user_prompt = (
            f"Original Python code:\n{python_code}\n\n"
            f"C++ translation:\n{cpp_code}\n\n"
            f"Test cases and expected outputs:\n{json.dumps(test_cases, indent=2)}\n\n"
            "Evaluate whether the C++ translation is correct and will produce identical output."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)
