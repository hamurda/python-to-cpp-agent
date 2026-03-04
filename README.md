# Python → C++ Translation Agent

Translates Python code to high-performance C++ using a 3-agent pipeline — no compiler required.

## The Problem

Translating Python to C++ for performance gains is straightforward with LLMs. Verifying the translation is harder, especially if you don't know C++. This project solves that with an agentic verification step: a second LLM generates test cases from the original Python, and a third evaluates the C++ translation against them.

## Pipeline

```
Python Code
    │
    ▼
┌─────────────┐
│  Translator │  Claude — translates Python to high-performance C++
└─────────────┘
    │
    ▼
┌──────────────────┐
│  Test Generator  │  GPT-4o — generates input/output test cases from the Python
└──────────────────┘
    │
    ▼
┌───────────┐
│ Evaluator │  GPT-4o — verifies C++ against test cases, checks for overflow/header issues
└───────────┘
    │
    ▼
Report + optimized.cpp
```

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

## Setup

```bash
pip install -r requirements.txt
```

Add a `.env` file:
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Examples

Two examples are included:

- **pi_calculation.py** — Leibniz formula for π, 100M iterations
- **max_subarray.py** — Maximum subarray sum with a custom LCG random number generator

Both are deliberately CPU-intensive Python scripts where C++ translation yields significant speedup.
