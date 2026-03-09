"""local-lm-arena: Streamlit web app for batch testing Ollama models."""

import copy
import io
import logging
import os
import time
import zipfile
from datetime import datetime

import ollama
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Local LM Arena",
    page_icon="\U0001f3df\ufe0f",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="lm_arena_errors.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------
DEFAULTS = {
    "step": 1,
    "questions": [],            # prompt strings sent to models
    "question_labels": [],      # display labels for results
    "question_cards": [         # card-based builder state
        {"id": 0, "text": "", "qtype": "Text", "language": "Python"},
    ],
    "_next_card_id": 1,         # monotonic counter for unique card IDs
    "timeout_per_question": 120, # seconds per question (0 = no limit)
    "selected_models": [],
    "output_dir": "./lm-arena-results",
    "results": {},          # model -> {responses, times, file}
    "running": False,
    "cancelled": False,
    "timestamp": "",
    "pull_status": None,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = copy.deepcopy(val)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def check_ollama_online() -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        ollama.list()
        return True
    except Exception:
        return False


def _extract_blob_dir(modelfile: str) -> str:
    """Extract the directory containing model blobs from the Modelfile FROM line."""
    for line in modelfile.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("FROM ") and ("blobs" in stripped or "models" in stripped):
            path = stripped[5:].strip()
            return os.path.dirname(path)
    return ""


def get_models() -> list[dict]:
    """Fetch installed Ollama models with blob directory info."""
    try:
        resp = ollama.list()
        models = []
        for m in resp.models:
            size_bytes = getattr(m, "size", 0) or 0
            size_gb = size_bytes / (1024 ** 3)
            size_str = (
                f"{size_gb:.1f} GB" if size_gb >= 1
                else f"{size_bytes / (1024**2):.0f} MB"
            )
            modified = getattr(m, "modified_at", None)
            if modified and hasattr(modified, "strftime"):
                mod_str = modified.strftime("%Y-%m-%d %H:%M")
            elif modified:
                mod_str = str(modified)
            else:
                mod_str = "N/A"
            # Get blob directory from modelfile
            blob_dir = ""
            try:
                info = ollama.show(m.model)
                modelfile = getattr(info, "modelfile", "") or ""
                blob_dir = _extract_blob_dir(modelfile)
            except Exception:
                pass
            models.append({
                "name": m.model,
                "size": size_str,
                "modified": mod_str,
                "blob_dir": blob_dir,
            })
        return models
    except Exception:
        return []


def write_model_markdown(
    filepath: str,
    model_name: str,
    questions: list[str],
    responses: list[str],
    times: list[float],
) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Model: {model_name}",
        f"**Test Date:** {now}",
        f"**Total Questions:** {len(questions)}",
        "",
        "---",
        "",
    ]
    for i, (q, a, t) in enumerate(zip(questions, responses, times), 1):
        lines += [
            f"## Question {i}",
            f"**Q:** {q}",
            "",
            "**A:**",
            a,
            "",
            f"*Response time: {t:.1f}s*",
            "",
            "---",
            "",
        ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_summary_markdown(
    filepath: str,
    models: list[str],
    questions: list[str],
    results: dict,
) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Test Summary",
        f"**Date:** {now}",
        f"**Total Questions:** {len(questions)}",
        "",
        "## Tested Models",
        "",
    ]
    for m in models:
        if m in results and results[m]["times"]:
            avg = sum(results[m]["times"]) / len(results[m]["times"])
            lines.append(f"- **{m}** - Avg response time: {avg:.1f}s")
        else:
            lines.append(f"- **{m}** - Skipped")
    lines += ["", "---", "", "## Side-by-Side Comparison", ""]
    for qi, q in enumerate(questions, 1):
        lines += [f"### Question {qi}", f"**Q:** {q}", ""]
        for m in models:
            if m not in results:
                continue
            r = results[m]["responses"][qi - 1] if qi - 1 < len(results[m]["responses"]) else "N/A"
            t = results[m]["times"][qi - 1] if qi - 1 < len(results[m]["times"]) else 0
            lines += [f"#### {m} ({t:.1f}s)", "", r, ""]
        lines += ["---", ""]
    lines += ["## Average Response Times", "", "| Model | Avg Response Time |", "|-------|-------------------|"]
    for m in models:
        if m in results and results[m]["times"]:
            avg = sum(results[m]["times"]) / len(results[m]["times"])
            lines.append(f"| {m} | {avg:.1f}s |")
        else:
            lines.append(f"| {m} | N/A |")
    lines.append("")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def build_zip(output_dir: str) -> bytes:
    """Create an in-memory ZIP of all .md files in the output directory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(output_dir)):
            if fname.endswith(".md"):
                zf.write(os.path.join(output_dir, fname), fname)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Sidebar: Ollama status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Ollama Status")
    online = check_ollama_online()
    if online:
        st.success("Online", icon="\u2705")
    else:
        st.error("Offline - start Ollama with `ollama serve`", icon="\u274c")

    st.divider()
    st.caption("local-lm-arena v1.0")

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("\U0001f3df\ufe0f Local LM Arena")

# ===================================================================
# STEP 1 - Setup
# ===================================================================
if st.session_state.step == 1:
    st.header("Step 1: Setup")

    # -- Questions (card-based builder) --
    st.subheader("Questions")

    cards = st.session_state.question_cards

    # Render each question card
    to_delete = None
    for i, card in enumerate(cards):
        cid = card["id"]  # stable unique ID for widget keys
        with st.container(border=True):
            header_cols = st.columns([0.85, 0.15])
            header_cols[0].markdown(f"**Question {i + 1}**")
            if header_cols[1].button(
                "\U0001f5d1\ufe0f", key=f"del_q_{cid}",
                help="Delete this question",
            ):
                to_delete = i

            is_code = card["qtype"] == "Code"
            if is_code:
                st.markdown(
                    "<style>.mono-next textarea{font-family:monospace!important}</style>"
                    '<div class="mono-next">',
                    unsafe_allow_html=True,
                )
            card["text"] = st.text_area(
                "Question text:",
                value=card["text"],
                height=100,
                key=f"q_text_{cid}",
                label_visibility="collapsed",
                placeholder=(
                    "Enter code here..." if is_code else "Enter your question here..."
                ),
            )
            if is_code:
                st.markdown("</div>", unsafe_allow_html=True)

            type_cols = st.columns([0.3, 0.3, 0.4])
            card["qtype"] = type_cols[0].selectbox(
                "Type",
                options=["Text", "Code"],
                index=0 if card["qtype"] == "Text" else 1,
                key=f"q_type_{cid}",
            )

            if card["qtype"] == "Code":
                card["language"] = type_cols[1].selectbox(
                    "Language",
                    options=["Python", "JavaScript", "SQL", "Bash", "Other"],
                    index=["Python", "JavaScript", "SQL", "Bash", "Other"].index(
                        card.get("language", "Python")
                    ),
                    key=f"q_lang_{cid}",
                )

    # Handle deletion (min 1 card)
    if to_delete is not None and len(cards) > 1:
        # Clean up widget keys for the deleted card
        dead_id = cards[to_delete]["id"]
        for prefix in ("q_text_", "q_type_", "q_lang_", "del_q_"):
            st.session_state.pop(f"{prefix}{dead_id}", None)
        cards.pop(to_delete)
        st.rerun()
    elif to_delete is not None:
        st.warning("You need at least 1 question card.")

    # Add question button
    if st.button("\u2795 Add Question"):
        new_id = st.session_state._next_card_id
        st.session_state._next_card_id = new_id + 1
        cards.append({"id": new_id, "text": "", "qtype": "Text", "language": "Python"})
        st.rerun()

    # Live counter
    filled = [c for c in cards if c["text"].strip()]
    st.caption(f"{len(filled)} question(s) added")

    st.divider()

    # -- Models --
    st.subheader("Models")
    models_list = get_models()

    if not models_list:
        st.warning("No models found. Pull a model below or check that Ollama is running.")

    selected: list[str] = []
    if models_list:
        for idx, m in enumerate(models_list):
            with st.container(border=True):
                row = st.columns([0.04, 0.36, 0.12, 0.18, 0.08])
                checked = row[0].checkbox(
                    "sel", key=f"model_chk_{idx}", label_visibility="collapsed"
                )
                row[1].markdown(f"**{m['name']}**")
                row[2].text(m["size"])
                row[3].text(m["modified"])
                if row[4].button(
                    "\U0001f5d1\ufe0f", key=f"model_del_{idx}",
                    help=f"Delete {m['name']} from system",
                ):
                    st.session_state["_confirm_delete_model"] = m["name"]

                # Show blob directory
                if m["blob_dir"]:
                    st.caption(f"\U0001f4c1 {m['blob_dir']}")

                if checked:
                    selected.append(m["name"])

        # Confirmation dialog for model deletion
        model_to_delete = st.session_state.get("_confirm_delete_model")
        if model_to_delete:
            st.warning(
                f"\u26a0\ufe0f **\"{model_to_delete}\"** modeli sistemden kalici olarak "
                f"silinecek. Bu islem geri alinamaz."
            )
            confirm_cols = st.columns([0.2, 0.2, 0.6])
            if confirm_cols[0].button(
                "\u2705 Evet, sil", key="confirm_del_model", type="primary"
            ):
                try:
                    ollama.delete(model_to_delete)
                    st.success(f"**{model_to_delete}** silindi.")
                except Exception as e:
                    st.error(f"Silinemedi: {e}")
                st.session_state.pop("_confirm_delete_model", None)
                st.rerun()
            if confirm_cols[1].button("\u274c Iptal", key="cancel_del_model"):
                st.session_state.pop("_confirm_delete_model", None)
                st.rerun()

    if len(selected) > 3:
        st.warning(
            "\u26a0\ufe0f You selected more than 3 models. The test may take a long time."
        )

    # -- Pull model --
    st.divider()
    st.subheader("Pull a New Model")
    pull_col1, pull_col2 = st.columns([0.7, 0.3])
    pull_name = pull_col1.text_input(
        "Model name to pull (e.g. llama3):",
        label_visibility="collapsed",
        placeholder="e.g. llama3",
    )
    if pull_col2.button("Pull Model", disabled=not pull_name):
        with st.spinner(f"Pulling {pull_name}... this may take a while"):
            try:
                ollama.pull(pull_name)
                st.success(f"Successfully pulled **{pull_name}**!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to pull model: {e}")

    st.divider()

    # -- Settings --
    st.subheader("Settings")
    settings_cols = st.columns([0.5, 0.5])
    with settings_cols[0]:
        timeout_val = st.number_input(
            "Timeout per question (seconds):",
            min_value=0,
            max_value=600,
            value=st.session_state.timeout_per_question,
            step=30,
            help="0 = no limit. Model will be stopped if it exceeds this time on a single question.",
        )
        st.session_state.timeout_per_question = timeout_val
    with settings_cols[1]:
        out_dir = st.text_input("Output directory:", value=st.session_state.output_dir)
        st.session_state.output_dir = out_dir

    st.divider()

    # -- Start button --
    can_start = len(filled) > 0 and len(selected) > 0 and online
    if st.button(
        "\u25b6\ufe0f  Start Test",
        type="primary",
        disabled=not can_start,
        use_container_width=True,
    ):
        # Build prompt strings and display labels from filled cards
        questions: list[str] = []
        question_labels: list[str] = []
        for card in filled:
            text = card["text"].strip()
            if card["qtype"] == "Code":
                lang = card.get("language", "Python").lower()
                prompt = (
                    f"Please answer the following {card.get('language', 'Python')} "
                    f"question:\n```{lang}\n{text}\n```"
                )
                questions.append(prompt)
                question_labels.append(f"[{card.get('language', 'Python')}] {text}")
            else:
                questions.append(text)
                question_labels.append(text)
        st.session_state.questions = questions
        st.session_state.question_labels = question_labels
        st.session_state.selected_models = selected
        st.session_state.results = {}
        st.session_state.cancelled = False
        st.session_state.running = True
        st.session_state.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(out_dir, exist_ok=True)
        st.session_state.step = 2
        st.rerun()

    if not online:
        st.info("Start Ollama to enable testing.")

# ===================================================================
# STEP 2 - Running
# ===================================================================
elif st.session_state.step == 2:
    st.header("Step 2: Running Tests")

    questions = st.session_state.questions
    models = st.session_state.selected_models
    output_dir = st.session_state.output_dir
    timestamp = st.session_state.timestamp
    total_tasks = len(models) * len(questions)

    # Cancel button at top
    cancel_placeholder = st.empty()

    progress_bar = st.progress(0, text="Starting...")
    completed = 0

    results: dict = {}

    for mi, model_name in enumerate(models):
        if st.session_state.cancelled:
            break

        status_label = f"Model {mi + 1}/{len(models)}: **{model_name}**"
        status_widget = st.status(status_label, expanded=True)

        with status_widget:
            # Warm up / load model
            st.write(f"Loading **{model_name}**...")
            try:
                ollama.chat(
                    model=model_name,
                    messages=[{"role": "user", "content": "hello"}],
                )
            except Exception as e:
                msg = f"Failed to load model '{model_name}': {e}"
                st.error(msg)
                logging.error(msg)
                status_widget.update(label=f"\u23ed\ufe0f Skipped: {model_name}", state="error")
                completed += len(questions)
                progress_bar.progress(
                    completed / total_tasks,
                    text=f"Skipped {model_name}",
                )
                continue

            model_responses: list[str] = []
            model_times: list[float] = []

            for qi, question in enumerate(questions):
                if st.session_state.cancelled:
                    break

                progress_bar.progress(
                    completed / total_tasks,
                    text=f"Model {mi + 1}/{len(models)} - Question {qi + 1}/{len(questions)}",
                )

                qlabels = st.session_state.get("question_labels", questions)
                qlabel = qlabels[qi] if qi < len(qlabels) else question
                st.markdown(f"---\n**Q{qi + 1}:** {qlabel}")

                timeout = st.session_state.get("timeout_per_question", 120)
                start = time.time()
                stream = None
                try:
                    stream = ollama.chat(
                        model=model_name,
                        messages=[{"role": "user", "content": question}],
                        stream=True,
                    )

                    # Stream with timeout and repetition detection
                    # Use a list so the nested generator can mutate it
                    chunks: list[str] = []
                    state = {"hit_limit": ""}

                    def token_generator():
                        recent_window = ""
                        for chunk in stream:
                            token = chunk.message.content
                            chunks.append(token)
                            # Timeout check
                            if timeout > 0 and (time.time() - start) > timeout:
                                state["hit_limit"] = "timeout"
                                return
                            # Repetition detection: check if the last ~200 chars
                            # contain a repeating pattern
                            recent_window += token
                            if len(recent_window) > 500:
                                recent_window = recent_window[-500:]
                            if len(recent_window) >= 200:
                                half = recent_window[len(recent_window) // 2:]
                                first_half = recent_window[:len(recent_window) // 2]
                                if len(half) > 80 and half[:80] in first_half:
                                    state["hit_limit"] = "repetition"
                                    return
                            yield token

                    response_text = st.write_stream(token_generator())
                    elapsed = time.time() - start
                    hit_limit = state["hit_limit"]

                    # If we hit a limit, close the stream to stop Ollama generation
                    # and ensure we move on cleanly to the next question
                    if hit_limit:
                        try:
                            stream.close()
                        except Exception:
                            pass
                        response_text = "".join(chunks)
                        if hit_limit == "timeout":
                            st.warning(
                                f"\u23f1\ufe0f Timeout ({timeout}s): skipping to next question. "
                                f"Partial response saved."
                            )
                        else:
                            st.warning(
                                "\U0001f501 Repetition detected: model looping. "
                                "Skipping to next question. Partial response saved."
                            )

                    model_responses.append(response_text)
                    model_times.append(elapsed)
                    st.caption(f"Response time: {elapsed:.1f}s")

                except Exception as e:
                    # Close stream on error too
                    if stream is not None:
                        try:
                            stream.close()
                        except Exception:
                            pass
                    elapsed = time.time() - start
                    err = f"Error on Q{qi + 1}: {e}"
                    st.error(err)
                    logging.error(f"{model_name} - {err}")
                    model_responses.append(f"Error: {e}")
                    model_times.append(elapsed)

                completed += 1

            # Save per-model markdown (use labels for display)
            labels = st.session_state.get("question_labels", questions)
            safe = model_name.replace(":", "_").replace("/", "_")
            fpath = os.path.join(output_dir, f"{safe}_{timestamp}.md")
            write_model_markdown(fpath, model_name, labels, model_responses, model_times)

            results[model_name] = {
                "responses": model_responses,
                "times": model_times,
                "file": fpath,
            }

            status_widget.update(
                label=f"\u2705 Done: {model_name}", state="complete", expanded=False
            )

    # Save summary (use labels for display)
    labels = st.session_state.get("question_labels", questions)
    summary_path = os.path.join(output_dir, f"summary_{timestamp}.md")
    write_summary_markdown(summary_path, models, labels, results)

    progress_bar.progress(1.0, text="All tests complete!")

    st.session_state.results = results
    st.session_state.running = False
    st.session_state.step = 3
    st.rerun()

# ===================================================================
# STEP 3 - Results
# ===================================================================
elif st.session_state.step == 3:
    st.header("Step 3: Results")

    questions = st.session_state.questions
    models = st.session_state.selected_models
    results = st.session_state.results
    output_dir = st.session_state.output_dir

    # -- Summary table --
    st.subheader("Summary")
    table_cols = st.columns([0.3, 0.2, 0.2, 0.3])
    table_cols[0].markdown("**Model**")
    table_cols[1].markdown("**Answered**")
    table_cols[2].markdown("**Avg Time**")
    table_cols[3].markdown("**Output File**")

    for m in models:
        c0, c1, c2, c3 = st.columns([0.3, 0.2, 0.2, 0.3])
        if m in results:
            data = results[m]
            answered = len(data["responses"])
            avg = (
                f"{sum(data['times']) / len(data['times']):.1f}s"
                if data["times"] else "N/A"
            )
            fname = os.path.basename(data["file"])
            c0.markdown(f"\u2705 {m}")
            c1.write(answered)
            c2.write(avg)
            c3.code(fname, language=None)
        else:
            c0.markdown(f"\u274c {m}")
            c1.write(0)
            c2.write("N/A")
            c3.write("Skipped")

    st.divider()

    # -- Side-by-side comparison per question --
    st.subheader("Answers by Question")

    active_models = [m for m in models if m in results]

    question_labels = st.session_state.get("question_labels", questions)
    for qi, question in enumerate(questions):
        display = question_labels[qi] if qi < len(question_labels) else question
        st.markdown(f"### Q{qi + 1}: {display}")

        if active_models:
            tabs = st.tabs(active_models)
            for tab, m in zip(tabs, active_models):
                with tab:
                    answer = results[m]["responses"][qi] if qi < len(results[m]["responses"]) else "N/A"
                    elapsed = results[m]["times"][qi] if qi < len(results[m]["times"]) else 0
                    st.caption(f"Response time: {elapsed:.1f}s")
                    st.markdown(answer)
        else:
            st.info("No model results available.")

        st.divider()

    # -- Action buttons --
    btn_col1, btn_col2, _ = st.columns([0.25, 0.25, 0.5])

    with btn_col1:
        zip_bytes = build_zip(output_dir)
        st.download_button(
            "\u2b07\ufe0f  Download All as ZIP",
            data=zip_bytes,
            file_name=f"lm-arena-results_{st.session_state.timestamp}.zip",
            mime="application/zip",
            use_container_width=True,
        )

    with btn_col2:
        if st.button(
            "\U0001f504  Run New Test",
            type="primary",
            use_container_width=True,
        ):
            # Clean up dynamic widget keys from old cards
            for card in st.session_state.get("question_cards", []):
                cid = card.get("id", 0)
                for prefix in ("q_text_", "q_type_", "q_lang_", "del_q_"):
                    st.session_state.pop(f"{prefix}{cid}", None)
            for key, val in DEFAULTS.items():
                st.session_state[key] = copy.deepcopy(val)
            st.rerun()
