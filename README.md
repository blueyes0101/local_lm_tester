# local-lm-arena

A batch testing tool that sends user-defined questions to multiple Ollama models sequentially, saving each model's responses to separate Markdown files for comparison.

Two interfaces are provided: a CLI tool (`main.py`) and a Streamlit web app (`app.py`).

![Setup Screen](docs/screenshot101.png)

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`)
- At least one model pulled locally (e.g. `ollama pull llama3`)

## Installation

```bash
cd local-lm-arena
pip install -r requirements.txt
```

## Usage

### Web App (Streamlit)

```bash
streamlit run app.py
```

The app opens in your browser with a 3-step wizard:

1. **Setup** - Build questions with the card-based editor, select models, configure timeout.
2. **Running** - Watch real-time streaming responses with progress tracking and automatic repetition/timeout detection.
3. **Results** - Compare answers side-by-side, download all results as ZIP.

### CLI

```bash
python main.py
```

Interactive terminal UI that walks you through question entry, model selection, and test execution.

## Output

- `<model_name>_<timestamp>.md` - Individual model results
- `summary_<timestamp>.md` - Side-by-side comparison with average response times

---

## Benchmark Results

All test results from the benchmark runs are available in this repository. You can browse them directly on GitHub or download the full repo.

### General Models — [`lm-arena-results/general/`](lm-arena-results/general/)

Tests across 30+ general-purpose Ollama models (8B–35B range), including Qwen3, Llama3, DeepSeek-R1, Granite, Phi4, Aya, Mistral and more.

| Document | Description |
|----------|-------------|
| [model_evaluation.md](docs/model_evaluation.md) | Detailed evaluation and scoring of all tested models |
| [model_guide.md](docs/model_guide.md) | Model comparison guide with recommendations |
| [model_evaluation_en.xlsx](docs/model_evaluation_en.xlsx) | Evaluation spreadsheet (v1) |
| [model_evaluation_en_v2.xlsx](docs/model_evaluation_en_v2.xlsx) | Evaluation spreadsheet (v2, updated) |

### Abliterated Models — [`lm-arena-results/abliterated/`](lm-arena-results/abliterated/)

Tests on uncensored/abliterated model variants (7B–32B), including huihui_ai series, Dolphin3, ExaOne-Deep, GPT-OSS, Mistral-Small, Phi4-Reasoning, QwQ and Qwen3-Coder abliterations.

| Document | Description |
|----------|-------------|
| [abliterated_model_report.xlsx](docs/abliterated_model_report.xlsx) | Full abliterated model benchmark report |

### Coding Models — [`lm-arena-coder-results/`](lm-arena-coder-results/)

Dedicated coding benchmark across 70+ models, organized into 4 tiers by parameter count:

| Tier | Size Range | Folder |
|------|-----------|--------|
| Kat A | 0.5B – 3.8B | [`lm-arena-coder-results/kat A/`](lm-arena-coder-results/kat%20A/) |
| Kat B | 6B – 9B | [`lm-arena-coder-results/kat B/`](lm-arena-coder-results/kat%20B/) |
| Kat C | 12B – 30B | [`lm-arena-coder-results/kat C/`](lm-arena-coder-results/kat%20C/) |
| Kat D | 22B – 34B | [`lm-arena-coder-results/kat D/`](lm-arena-coder-results/kat%20D/) |

Models tested include: CodeGemma, CodeLlama, DeepSeek-Coder, DeepCoder, StarCoder2, OpenCoder, Granite-Code, Qwen2.5-Coder, Qwen3-Coder, Devstral, Codestral, Magistral, ExaOne-Deep, WizardLM2, and more.

| Document | Description |
|----------|-------------|
| [fullstack_results_en.xlsx](docs/fullstack_results_en.xlsx) | Full coding benchmark results and analysis |
