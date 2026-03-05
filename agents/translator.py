import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

SYSTEM_MESSAGE = (
    "You are an expert C++ developer. Your job is to translate Python code into "
    "high-performance C++ that produces identical output. "
    "Respond only with C++ code. Use comments sparingly. "
    "Pay attention to number types to avoid integer overflows. "
    "Include all necessary headers."
)

FIX_SYSTEM_MESSAGE = (
    "You are an expert C++ developer. You will receive a C++ translation of Python code "
    "that has issues identified by a code reviewer. Fix the issues while keeping the code "
    "high-performance. Respond only with the corrected C++ code."
)


class Translator:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = model

    def run(self, python_code: str) -> str:
        user_prompt = (
            "Translate this Python code to high-performance C++. "
            "The C++ must produce identical output. "
            "Respond only with C++ code.\n\n"
            f"{python_code}"
        )

        result = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_MESSAGE,
                temperature=0.1,
            )
        )

        cpp_code = result.text
        return cpp_code.replace("```cpp", "").replace("```", "").strip()
    
    def fix(self, python_code: str, cpp_code: str, issues: list[str]) -> str:
        issues_text = "\n".join(f"- {issue}" for issue in issues)

        user_prompt = (
            f"Original Python code:\n{python_code}\n\n"
            f"Current C++ translation:\n{cpp_code}\n\n"
            f"Issues found by reviewer:\n{issues_text}\n\n"
            "Fix these issues. The C++ must produce identical output to the Python. "
            "Respond only with the corrected C++ code."
        )

        result = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=FIX_SYSTEM_MESSAGE,
                temperature=0.1,
            )
        )

        cpp_code = result.text
        return cpp_code.replace("```cpp", "").replace("```", "").strip()
