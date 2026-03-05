import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_MESSAGE = (
    "You are a software testing expert. Your job is to generate test cases that verify "
    "a C++ translation produces the same computational results as the original Python code. "
    "Focus on the actual values the code computes with its real parameters — not edge cases, "
    "not exception handling, not formatting. The goal is to check mathematical/logical correctness. "
    "For each test case, describe what the code should compute and what the expected numerical "
    "result is when run with the parameters as written in the source code. "
    "Respond only in valid JSON — no preamble, no markdown fences. "
    "Format: {\"test_cases\": [{\"description\": str, \"expected_output\": str, \"logic_tested\": str}]}"
)


class TestGenerator:
    def __init__(self, model: str = "gpt-5-mini"):
        self.client = OpenAI()
        self.model = model

    def run(self, python_code: str) -> dict:
        user_prompt = (
            "Generate 3 test cases for this Python code that verify computational correctness. "
            "Use the actual parameters from the code as written — do not invent edge cases "
            "or hypothetical inputs. Focus on: does the core algorithm produce the right numerical "
            "result? Ignore output formatting, print prefixes, and exception handling.\n\n"
            f"{python_code}"
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
