# Local LM Arena — LM Studio Backend Upgrade

## 1. Overview

Local LM Arena is a Streamlit web app for batch-testing local LLMs: you define a
set of questions, pick one or more locally available models, run them, and review
the answers side by side (with per-model and summary Markdown exports). As of this
upgrade the app supports **two backends** — **Ollama** (the original) and **LM Studio**
(OpenAI-compatible API) — selectable at the top of the setup screen. All existing
Ollama functionality is unchanged.

## 2. Backends

| Aspect | Ollama | LM Studio |
|--------|--------|-----------|
| Connection method | Local `ollama` Python client | HTTP REST (`requests`) to an OpenAI-compatible server |
| Default endpoint | Local Ollama daemon (`ollama serve`) | `http://localhost:1234` (configurable) |
| Model source | Installed Ollama models (`ollama.list()`) | `GET /v1/models` on the LM Studio server |
| Streaming | Yes (`stream=True`, live token output) | No (single non-streaming `POST`, shown after completion) |
| Delete model from UI | Yes | No (remote models are not deletable) |
| Pull / download model | Yes (`ollama.pull`) | No (manage models inside LM Studio) |
| Warm-up ping | Yes (loads model with a "hello" before testing) | No (model loads on first request) |
| Repetition detection | Yes (streaming guard) | No (non-streaming, not applicable) |

## 3. What Was Added

The LM Studio integration extends the existing 3-step wizard without altering the
Ollama path:

- **Backend selector** — an `st.radio` at the very top of Step 1 chooses between
  Ollama and LM Studio.
- **LM Studio connection panel** (shown only when LM Studio is selected) — a
  **Base URL** input (default `http://localhost:1234`), an optional **API Key**
  (password field; sent as `Authorization: Bearer <key>` only when provided), and a
  **Connect & Fetch Models** button that calls `GET {base_url}/v1/models` with a
  10-second timeout. Success shows a green **Connected** badge and populates the
  model list; failure shows a red error with the HTTP status or exception message.
- **Model cards** — fetched models are listed in the same card style as Ollama,
  showing the model **id** and **`owned_by`** (when present), selectable via the
  same checkboxes. There is **no delete button** and **no blob/path line** (neither
  applies to remote models).
- **Sidebar status** — switches per backend: Ollama shows Online/Offline; LM Studio
  shows Connected/Not connected.
- **Execution path** (Step 2) — for LM Studio, each question is sent as a
  non-streaming `POST {base_url}/v1/chat/completions`
  (`stream: false`, `temperature: 0.7`, `max_tokens: 2048`). A spinner is shown
  while waiting, the full response is rendered with `st.markdown`, and on
  `requests.exceptions.Timeout` the answer is recorded as `"TIMEOUT"` and the run
  continues. The Ollama-only **warm-up ping** and **repetition detection** are
  skipped. The per-question timeout setting is reused as the `requests` timeout
  (`0` = no limit).
- **Summary Markdown** — the summary header now records the backend, e.g.
  `**Backend:** LM Studio (http://localhost:1234)` or `**Backend:** Ollama`.

## 4. New Session State Keys

All keys are initialized in the `DEFAULTS` dictionary at the top of `app.py`.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend` | str | `"ollama"` | `"ollama"` or `"lmstudio"` |
| `lmstudio_base_url` | str | `"http://localhost:1234"` | LM Studio server URL |
| `lmstudio_api_key` | str | `""` | Optional API key |
| `lmstudio_connected` | bool | `False` | Whether connection was verified |
| `lmstudio_models` | list | `[]` | Models fetched from LM Studio |

## 5. How to Use

**With Ollama (unchanged):**
1. Start Ollama (`ollama serve`).
2. Leave the backend set to **Ollama**.
3. Add questions, select one or more installed models, set the timeout, and click
   **Start Test**.

**With LM Studio:**
1. Start the LM Studio local server and load at least one model.
2. At the top of Step 1, set the backend to **LM Studio**.
3. Enter the **Base URL** (default `http://localhost:1234`) and, if required, an
   API key.
4. Click **Connect & Fetch Models**; confirm the green **Connected** badge.
5. Select the models to test, add questions, set the timeout, and click
   **Start Test**.

Results, the side-by-side comparison, per-model Markdown files, the summary file,
and the ZIP download behave the same for both backends.

## 6. Verification

The upgrade was verified before release:

- `py_compile` passes for `app.py` (and `main.py` is unchanged).
- Stubbed end-to-end happy paths for **both** backends (connect → fetch → select →
  run → results, plus the correct `**Backend:**` summary header).
- No regressions to the Ollama path (cards, delete, blob path, pull, streaming
  output, timeout/repetition handling all preserved).
- An adversarial multi-lens review produced four confirmed findings, all fixed and
  re-verified with Streamlit's `AppTest`:
  1. Sidebar reflects the active backend on the same run as a backend switch.
  2. "Run New Test" fully resets the backend selector and stale model selections.
  3. Each LM Studio fetch clears prior checkbox state (no stale/mismatched
     selections after a reconnect).
  4. `lmstudio_chat` surfaces the server's own error message on a 2xx error body
     instead of an opaque `KeyError`.
