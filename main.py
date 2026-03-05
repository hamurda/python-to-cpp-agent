import argparse
from pathlib import Path
from dotenv import load_dotenv
from agents import Translator, TestGenerator, Evaluator

load_dotenv()

MAX_RETRIES = 3

def print_report(cpp_code: str, test_cases: dict, evaluation: dict):
    verdict = evaluation.get("verdict", "UNKNOWN")
    confidence = evaluation.get("confidence", 0)
    issues = evaluation.get("issues", [])
    summary = evaluation.get("summary", "")

    verdict_color = {
        "PASS": "\033[92m",  # green
        "WARN": "\033[93m",  # yellow
        "FAIL": "\033[91m",  # red
    }.get(verdict, "\033[0m")
    reset = "\033[0m"

    print("\n" + "=" * 60)
    print("  PYTHON → C++ TRANSLATION REPORT")
    print("=" * 60)

    print("\n📝 GENERATED C++ CODE")
    print("-" * 60)
    print(cpp_code)

    print("\n🧪 TEST CASES")
    print("-" * 60)
    for i, tc in enumerate(test_cases.get("test_cases", []), 1):
        print(f"\n  Test {i}: {tc.get('description', '')}")
        print(f"  Expected output : {tc.get('expected_output', '')}")
        print(f"  Logic tested    : {tc.get('logic_tested', '')}")

    print("\n📊 EVALUATION")
    print("-" * 60)
    print(f"  Verdict    : {verdict_color}{verdict}{reset}")
    print(f"  Confidence : {confidence}%")
    print(f"  Summary    : {summary}")
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(f"    ⚠️  {issue}")

    print("\n" + "=" * 60)


def save_cpp(cpp_code: str, output_path: str = "output/optimized.cpp"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(cpp_code)
    print(f"\n💾 C++ file saved to: {output_path}")


def run_pipeline(python_code: str, output_path: str = "output/optimized.cpp"):
    translator = Translator()
    test_generator = TestGenerator()
    evaluator = Evaluator()

    print("\n🔄 Step 1/3: Translating Python → C++...")
    cpp_code = translator.run(python_code)

    print("🧪 Step 2/3: Generating test cases...")
    test_cases = test_generator.run(python_code)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"🔍 Step 3: Evaluating translation (attempt {attempt}/{MAX_RETRIES})...")
        evaluation = evaluator.run(python_code, cpp_code, test_cases)

        verdict = evaluation.get("verdict", "UNKNOWN")
        confidence = evaluation.get("confidence", 0)
        if verdict == "PASS":
            print(f"✅ Translation passed evaluation on attempt {attempt}.")
            break

        if attempt < MAX_RETRIES:
            issues = evaluation.get("issues", [])
            summary = evaluation.get("summary", "Translation has issues.")
            all_feedback = issues if issues else [summary]
            print(f"⚠️  Verdict: {verdict} — sending feedback to translator...")
            cpp_code = translator.fix(python_code, cpp_code, all_feedback)
        else:
            print(f"⚠️  Verdict: {verdict} after {MAX_RETRIES} attempts. Returning best effort.")

    save_cpp(cpp_code, output_path)
    print_report(cpp_code, test_cases, evaluation)

    return cpp_code, test_cases, evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate Python to C++ with agentic verification")
    parser.add_argument("input", help="Path to Python file to translate")
    parser.add_argument("--output", default="output/optimized.cpp", help="Output path for C++ file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        python_code = f.read()

    run_pipeline(python_code, args.output)
