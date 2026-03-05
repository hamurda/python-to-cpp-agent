# Python → C++ Translation Agent

A 3-agent pipeline that translates Python to C++ and verifies correctness, no compiler required.

## The Problem

LLMs can generate or translate code fairly well. This project builds an agentic 
verification loop around the translation step: one LLM translates, a second generates 
test expectations from the source Python, and a third evaluates the translation against those expectations. 
If the evaluation fails, the issues are fed back to the translator for another attempt, up to 3
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
    └── FAIL/WARN → feed issues back to Translator (up to 3 attempts)

```

The translator and evaluator use different LLMs deliberately — if the same model
translates and evaluates, it tends to confirm its own mistakes. Model choices are
cost-driven; the architecture is model-agnostic so swapping in stronger models
is a config change.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OpenAI + Gemini api keys
python main.py examples/pi_calculation.py --output output/pi.cpp
```

Or run the Gradio UI: `python app.py`

Two CPU-intensive examples are included: Leibniz π approximation (100M iterations)
and maximum subarray sum with a custom RNG.

## Background

This started as an exercise from Ed Donner's LLM Engineering course, where the
task is to translate Python to C++ using an LLM and manually compile to verify.
The two example scripts in `examples/` are from the course material.

I wanted to automate verification without leaving Python; the agentic feedback
loop, test generator, and evaluator are my additions to the original exercise.

## Limitations

The evaluator does static analysis only. It reasons about the C++ but never
executes it. The test generator predicts what the Python should output rather
than running it. For the included examples (pure math, deterministic), this works
well. For complex code, you'd want actual execution; e.g. OpenAI's Code Interpreter
for Python ground truth, or a Docker container for C++ compilation.



## Example Output

```
🔄 Step 1: Translating Python → C++...
🧪 Step 2: Generating test cases...
🔍 Step 3: Evaluating translation (attempt 1/3)...
✅ Translation passed evaluation on attempt 1.

📝 GENERATED C++ CODE
------------------------------------------------------------
#include <iostream>   // Required for input/output operations (std::cout, std::endl)
#include <chrono>     // Required for time measurement (std::chrono::high_resolution_clock)...

============================================================
  PYTHON → C++ TRANSLATION REPORT
============================================================
🧪 TEST CASES
------------------------------------------------------------

  Test 1: Run the program as written: compute result = calculate(100000000, 4, 1) * 4 and...


📊 EVALUATION
------------------------------------------------------------
  Verdict    : PASS
  Confidence : 90%
  Summary    : The C++ code implements the same algorithm as the Python code: 
               it iterates i=1..iterations, computes (1/(i*param1+param2) - 1/(i*param1-param2))
               accumulated into a double starting from 1.0, and multiplies 4.0 in main...


  Issues found:
    ⚠️  The translation uses the single-quote digit separator in the literal 100'000'000LL 
        which requires a C++14 (or newer) compiler. This is a compilation-standard...
    
============================================================
```
