# local-lm-arena

A batch testing tool for running questions against multiple local Ollama models simultaneously, comparing their responses side by side and saving results as Markdown files.

![Setup Screen](docs/screenshot101.png)

---

## Features

- **Card-based question builder** — Add/remove questions individually, set type (Text or Code), choose language for code questions
- **Batch testing** — Test multiple models in one run, results saved per model and as a combined summary
- **Real-time streaming** — Watch responses appear token by token with progress tracking
- **Timeout & loop detection** — Configurable per-question timeout; automatic repetition detection stops looping models and moves on
- **Model management** — View installed models with file path and size, delete models directly from the UI
- **Two interfaces** — Streamlit web app (`app.py`) and interactive CLI (`main.py`)

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`)
- At least one model pulled (e.g. `ollama pull llama3`)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web App

```bash
streamlit run app.py
```

3-step wizard: **Setup → Running → Results**

### CLI

```bash
python main.py
```

---

## Benchmark Results

All results from benchmark runs are available in [`lm-arena-results/`](lm-arena-results/).

### General Models — [`lm-arena-results/general/`](lm-arena-results/general/)

40 general-purpose models tested (8B–35B): Qwen3, Llama3, DeepSeek-R1, Granite, Phi4, Aya, Mistral, StableLM, Yi and more.

| File | Description |
|------|-------------|
| [model_evaluation.md](docs/model_evaluation.md) | Scoring and evaluation of all tested models |
| [model_guide.md](docs/model_guide.md) | Model comparison guide and recommendations |
| [model_evaluation_en.xlsx](docs/model_evaluation_en.xlsx) | Evaluation spreadsheet (v1) |
| [model_evaluation_en_v2.xlsx](docs/model_evaluation_en_v2.xlsx) | Evaluation spreadsheet (v2) |

### Abliterated Models — [`lm-arena-results/abliterated/`](lm-arena-results/abliterated/)

15 uncensored/abliterated variants tested (3.8B–32B): huihui_ai series, Dolphin3, ExaOne-Deep, GPT-OSS, Mistral-Small, Phi4-Reasoning, QwQ, Qwen3-Coder and others.

| File | Description |
|------|-------------|
| [abliterated_model_report.xlsx](docs/abliterated_model_report.xlsx) | Full abliterated model benchmark report |

### Coding Models — [`lm-arena-results/coder/`](lm-arena-results/coder/)

80 coding-focused models benchmarked across 4 size tiers:

| Tier | Size | Models | Folder |
|------|------|--------|--------|
| Kat A | 0.5B – 3.8B | 28 | [`coder/kat A/`](lm-arena-results/coder/kat%20A/) |
| Kat B | 6B – 9B | 18 | [`coder/kat B/`](lm-arena-results/coder/kat%20B/) |
| Kat C | 12B – 30B | 14 | [`coder/kat C/`](lm-arena-results/coder/kat%20C/) |
| Kat D | 22B – 34B | 20 | [`coder/kat D/`](lm-arena-results/coder/kat%20D/) |

Models include: CodeGemma, CodeLlama, DeepSeek-Coder, DeepCoder, StarCoder2, OpenCoder, Granite-Code, Qwen2.5-Coder, Qwen3-Coder, Devstral, Codestral, Magistral, ExaOne-Deep, WizardLM2, QwQ and more.

| File | Description |
|------|-------------|
| [fullstack_results_en.xlsx](docs/fullstack_results_en.xlsx) | Full coding benchmark analysis and scores |

---

## Output Format

Each test run produces:
- `<model>_<timestamp>.md` — per-model responses with timing
- `summary_<timestamp>.md` — side-by-side comparison across all models
