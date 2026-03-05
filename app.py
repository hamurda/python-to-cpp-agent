import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
from agents import Translator, TestGenerator, Evaluator

load_dotenv()

PI_EXAMPLE = open("examples/pi_calculation.py").read()
SUBARRAY_EXAMPLE = open("examples/max_subarray.py").read()

MAX_RETRIES = 3


def run_pipeline(python_code: str):
    if not python_code.strip():
        return "No input provided.", "", "", ""

    try:
        translator = Translator()
        test_generator = TestGenerator()
        evaluator = Evaluator()

        yield "🔄 Translating Python → C++...", "", "", ""
        cpp_code = translator.run(python_code)

        yield "🧪 Generating test cases...", cpp_code, "", ""
        test_cases = test_generator.run(python_code)

        for attempt in range(1, MAX_RETRIES + 1):
            yield (
                f"🔍 Evaluating translation (attempt {attempt}/{MAX_RETRIES})...",
                cpp_code,
                format_test_cases(test_cases),
                "",
            )
            evaluation = evaluator.run(python_code, cpp_code, test_cases)

            verdict = evaluation.get("verdict", "UNKNOWN")
            if verdict == "PASS":
                break

            if attempt < MAX_RETRIES:
                issues = evaluation.get("issues", [])
                summary = evaluation.get("summary", "Translation has issues.")
                all_feedback = issues if issues else [summary]

                yield (
                    f"🔧 Attempt {attempt} got {verdict} — fixing issues...",
                    cpp_code,
                    format_test_cases(test_cases),
                    format_evaluation(evaluation),
                )
                cpp_code = translator.fix(python_code, cpp_code, all_feedback)

        save_cpp(cpp_code)

        status = f"✅ Passed on attempt {attempt}!" if verdict == "PASS" else f"⚠️ Best effort after {MAX_RETRIES} attempts ({verdict})"
        yield status, cpp_code, format_test_cases(test_cases), format_evaluation(evaluation)

    except Exception as e:
        yield f"❌ Error: {str(e)}", "", "", ""


def format_test_cases(test_cases: dict) -> str:
    lines = []
    for i, tc in enumerate(test_cases.get("test_cases", []), 1):
        lines.append(f"Test {i}: {tc.get('description', '')}")
        lines.append(f"  Expected output : {tc.get('expected_output', '')}")
        lines.append(f"  Logic tested    : {tc.get('logic_tested', '')}")
        lines.append("")
    return "\n".join(lines)


def format_evaluation(evaluation: dict) -> str:
    verdict = evaluation.get("verdict", "UNKNOWN")
    confidence = evaluation.get("confidence", 0)
    summary = evaluation.get("summary", "")
    issues = evaluation.get("issues", [])

    lines = [
        f"Verdict    : {verdict}",
        f"Confidence : {confidence}%",
        f"Summary    : {summary}",
    ]
    if issues:
        lines.append("\nIssues found:")
        for issue in issues:
            lines.append(f"  ⚠️  {issue}")
    return "\n".join(lines)


def save_cpp(cpp_code: str):
    Path("output").mkdir(exist_ok=True)
    with open("output/optimized.cpp", "w") as f:
        f.write(cpp_code)


with gr.Blocks(title="Python → C++ Agent", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# Python → C++ Translation Agent")
    gr.Markdown(
        "Paste Python code below. The pipeline will translate it to C++, "
        "generate test cases, and evaluate the translation — no compiler needed."
    )

    with gr.Row():
        with gr.Column():
            python_input = gr.Code(
                label="Python Code",
                language="python",
                value=PI_EXAMPLE,
                lines=20,
            )
            with gr.Row():
                example_pi = gr.Button("Load Pi Example")
                example_sub = gr.Button("Load Subarray Example")
            run_btn = gr.Button("Run Pipeline", variant="primary")

        with gr.Column():
            status = gr.Textbox(label="Status", interactive=False)
            cpp_output = gr.Code(label="Generated C++", language="cpp", lines=20)

    with gr.Row():
        test_output = gr.Textbox(label="Test Cases", lines=10, interactive=False)
        eval_output = gr.Textbox(label="Evaluation Report", lines=10, interactive=False)

    run_btn.click(
        fn=run_pipeline,
        inputs=[python_input],
        outputs=[status, cpp_output, test_output, eval_output],
    )
    example_pi.click(fn=lambda: PI_EXAMPLE, outputs=[python_input])
    example_sub.click(fn=lambda: SUBARRAY_EXAMPLE, outputs=[python_input])

if __name__ == "__main__":
    demo.launch()
