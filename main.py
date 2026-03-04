import argparse
from pathlib import Path
from agents import Translator, TestGenerator, Evaluator


def print_report(python_code: str, cpp_code: str, test_cases: dict, evaluation: dict):
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
    print("\n🔄 Step 1/3: Translating Python → C++...")
    translator = Translator()
    cpp_code = translator.run(python_code)

    print("🧪 Step 2/3: Generating test cases...")
    test_generator = TestGenerator()
    test_cases = test_generator.run(python_code)

    print("🔍 Step 3/3: Evaluating translation...")
    evaluator = Evaluator()
    evaluation = evaluator.run(python_code, cpp_code, test_cases)

    save_cpp(cpp_code, output_path)
    print_report(python_code, cpp_code, test_cases, evaluation)

    return cpp_code, test_cases, evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate Python to C++ with agentic verification")
    parser.add_argument("input", help="Path to Python file to translate")
    parser.add_argument("--output", default="output/optimized.cpp", help="Output path for C++ file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        python_code = f.read()

    run_pipeline(python_code, args.output)
