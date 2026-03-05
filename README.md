# Python → C++ Translation Agent

A 3-agent pipeline that translates Python to C++ and verifies correctness, no compiler required.

## The Problem

LLMs can generate or translate code fairly well. Knowing whether the output is
correct is a different problem entirely. You'd normally need to install a compiler,
write test harnesses, and run both versions to compare. If you don't know the
target language, you might not even recognize a wrong answer.

This project builds an agentic verification loop around the translation step:
one LLM translates, a second generates test expectations from the source Python,
and a third evaluates the translation against those expectations. If the evaluation
fails, the issues are fed back to the translator for another attempt, up to 3
iterations until it passes or returns its best effort.

## How It Works

```
Python Code
    │
    ▼
┌─────────────┐
│  Translator │  Gemini — translates Python to optimized C++
└─────────────┘
    │
    ▼
┌──────────────────┐
│  Test Generator  │  GPT-5-Mini — reads the Python, produces expected behaviors
└──────────────────┘
    │
    ▼
┌───────────────┐
│   Evaluator   │  GPT-5-Mini — checks the C++ against expectations, flags issues
└───────────────┘
    │
    ├── PASS → done, save optimized.cpp
    │
    └── FAIL/WARN → feed issues back to Translator
         │
         └── retry (up to 3 attempts)
```

**Why different models?** The translator and evaluator use different LLMs deliberately.
If the same model translates and evaluates, it tends to confirm its own mistakes.
Using Gemini for translation and GPT 5 Mini for verification adds a genuine second opinion.

**Model choices are cost-driven.** Gemini 2.5 Flash handles translation well at a
fraction of Claude Opus pricing and still doing reasonably well in leaderboards. 
Similarly, GPT-5-Mini is still strong at structured evaluation with JSON output.
With more budget or local GPU capacity, you could swap in stronger models from the
leaderboards, the agent architecture is model-agnostic, so upgrading is a config change.
Open-source models like CodeLlama or DeepSeek-Coder are options if you have the
hardware, but the models large enough for reliable code translation don't run
comfortably on consumer machines.

## Usage

### CLI

```bash
python main.py examples/pi_calculation.py
python main.py examples/max_subarray.py --output output/subarray.cpp
```

### Gradio UI

```bash
python app.py
```

Opens a local interface with the Python input pre-filled, three output panels
(generated C++, test cases, evaluation report), and a file download for the `.cpp`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
```

## Examples

Two scripts are included, both deliberately CPU-intensive so C++ translation
yields meaningful speedup:

- **pi_calculation.py** — Leibniz formula for π, 100M iterations
- **max_subarray.py** — Maximum subarray sum using a custom LCG random number generator

## Background

This started as an exercise from Ed Donner's LLM Engineering course, where the
task is to translate Python to C++ using an LLM and manually compile to verify.
The two example scripts in `examples/` are from the course material.

I wanted to automate the verification step, partly because I don't write C++, and
partly because "generate and hope" isn't how I'd build a real pipeline. The test
generator, evaluator, and the feedback loop that iterates until the code passes
are my additions to the original exercise.

## Limitations and Future Work

**Current approach: static analysis only.** The evaluator reads the C++ and reasons
about correctness, but never executes anything. The test generator predicts what
the Python *should* output rather than actually running it. This means the entire
verification chain is LLM reasoning.

For the included examples (pure math, deterministic output), this works well.
For more complex code, the lack of execution is a real gap.

**What would make this stronger:**

- **Execute the Python** using OpenAI's Code Interpreter to get real output,
  then evaluate the C++ against actual results instead of predicted ones.
  This eliminates the weakest link, the test generator guessing wrong.
- **Add a compilation step** using a remote compiler API or Docker container,
  so the C++ is actually built and run rather than just reviewed.
- **Test with harder examples**, longer scripts with non-trivial state,
  file I/O, or edge cases where static analysis is more likely to miss issues.

The current version is a working proof of concept for the multi-agent verification
pattern. The architecture would stay the same with these improvements, you'd
just be swapping in stronger verification agents.

## Project Structure

```
python-to-cpp-agent/
├── main.py              # CLI entry point
├── app.py               # Gradio UI
├── agents/
│   ├── __init__.py
│   ├── translator.py    # Gemini 2.5 Flash — Python to C++ translation
│   ├── test_generator.py # GPT 5 Mini — generates test cases from Python
│   └── evaluator.py     # GPT 5 Mini — verifies C++ against test cases
├── examples/
│   ├── pi_calculation.py
│   └── max_subarray.py
├── .env.example
├── requirements.txt
└── README.md
```

## Example Output

```
🔄 Step 1: Translating Python → C++...
🧪 Step 2: Generating test cases...
🔍 Step 3: Evaluating translation (attempt 1/3)...
✅ Translation passed evaluation on attempt 1.

📝 GENERATED C++ CODE
------------------------------------------------------------
#include <iostream>   // Required for input/output operations (std::cout, std::endl)
#include <chrono>     // Required for time measurement (std::chrono::high_resolution_clock)
#include <iomanip>    // Required for output formatting (std::fixed, std::setprecision)

....

============================================================
  PYTHON → C++ TRANSLATION REPORT
============================================================
🧪 TEST CASES
------------------------------------------------------------

  Test 1: Run the program as written: compute result = calculate(100000000, 4, 1) * 4 and print it with 12 decimal places. This verifies the full loop and the final scaling by 4 produce the known limiting value (the series converges to π).
  Expected output : 3.141592653590
  Logic tested    : Full numeric result of the main loop and scaling: 4 * (1 + sum_{i=1..100000000} (1/(4*i+1) - 1/(4*i-1))) ≈ π; check printed .12f value.

  Test 2: Check the raw...


📊 EVALUATION
------------------------------------------------------------
  Verdict    : PASS
  Confidence : 90%
  Summary    : The C++ code implements the same algorithm as the Python code: 
               it iterates i=1..iterations, computes (1/(i*param1+param2) - 1/(i*param1-param2))
               accumulated into a double starting from 1.0, and multiplies 4.0 in main. Types 
               and operation order match the Python behavior (Python floats are IEEE double),
               there is no risk of integer overflow...


  Issues found:
    ⚠️  The translation uses the single-quote digit separator in the literal 100'000'000LL 
        which requires a C++14 (or newer) compiler. This is a compilation-standard note, 
        not a numerical correctness issue.
    ⚠️  The program prints the result with a leading label...
    
============================================================
```