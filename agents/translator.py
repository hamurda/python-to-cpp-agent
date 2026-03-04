import anthropic

SYSTEM_MESSAGE = (
    "You are an expert C++ developer. Your job is to translate Python code into "
    "high-performance C++ that produces identical output. "
    "Respond only with C++ code. Use comments sparingly. "
    "Pay attention to number types to avoid integer overflows. "
    "Include all necessary headers."
)


class Translator:
    def __init__(self, model: str = "claude-opus-4-5"):
        self.client = anthropic.Anthropic()
        self.model = model

    def run(self, python_code: str) -> str:
        user_prompt = (
            "Translate this Python code to high-performance C++. "
            "The C++ must produce identical output. "
            "Respond only with C++ code.\n\n"
            f"{python_code}"
        )

        result = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SYSTEM_MESSAGE,
            messages=[{"role": "user", "content": user_prompt}],
        )

        cpp_code = result.content[0].text
        return cpp_code.replace("```cpp", "").replace("```", "").strip()
