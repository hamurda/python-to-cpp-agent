from openai import OpenAI

SYSTEM_MESSAGE = (
    "You are a software testing expert. Your job is to generate test cases for Python code. "
    "For each test case, provide: a description, the expected output, and the key logic being tested. "
    "Respond only in valid JSON — no preamble, no markdown fences. "
    "Format: {\"test_cases\": [{\"description\": str, \"expected_output\": str, \"logic_tested\": str}]}"
)


class TestGenerator:
    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    def run(self, python_code: str) -> dict:
        user_prompt = (
            "Generate 3 test cases for this Python code. "
            "Focus on the expected output values and edge cases.\n\n"
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

        import json
        return json.loads(response.choices[0].message.content)
