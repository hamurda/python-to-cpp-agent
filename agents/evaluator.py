from openai import OpenAI
import json

SYSTEM_MESSAGE = (
    "You are a C++ code reviewer. Your job is to evaluate whether a C++ translation "
    "of Python code is correct, without executing it. "
    "You will be given the original Python code, the C++ translation, and test cases with expected outputs. "
    "Check for: logical equivalence, integer overflow risks, missing headers, and output format correctness. "
    "Respond only in valid JSON — no preamble, no markdown fences. "
    "Format: {\"verdict\": \"PASS\" | \"FAIL\" | \"WARN\", \"confidence\": int (0-100), "
    "\"issues\": [str], \"summary\": str}"
)


class Evaluator:
    def __init__(self, model: str = "gpt-4o"):
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
