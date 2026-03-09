#!/usr/bin/env python3
"""local-lm-arena: Batch testing tool for comparing Ollama model responses."""

import os
import subprocess
import sys
import time
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text
from rich import box

import ollama

console = Console()

BANNER = r"""
  _                    _   _     __  __     _
 | |   ___  __ __ _ _ | | | |   |  \/  |   /_\  _ _ ___ _ _  __ _
 | |__/ _ \/ _/ _` | || | | |__ | |\/| |  / _ \| '_/ -_) ' \/ _` |
 |____\___/\__\__,_|\_,_| |____||_|  |_| /_/ \_\_| \___|_||_\__,_|
"""


def show_welcome():
    """Display the welcome banner."""
    console.print(Panel(
        Text(BANNER, style="bold cyan", justify="center"),
        title="[bold cyan]local-lm-arena[/bold cyan]",
        subtitle="[dim]Batch LLM Testing Tool for Ollama[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()


def collect_questions() -> list[str]:
    """Collect questions from the user, one per line."""
    console.print(
        Panel(
            "[cyan]Enter the questions you want to test (one per line).\n"
            "Press Enter twice when done.[/cyan]",
            title="[bold cyan]Question Input[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    questions: list[str] = []
    while True:
        prompt_text = f"  [dim]Q{len(questions) + 1}:[/dim] "
        try:
            line = console.input(prompt_text).strip()
        except EOFError:
            break
        if not line:
            break
        questions.append(line)
        console.print(f"    [green]Added question {len(questions)}[/green]")

    if not questions:
        console.print("[red]Error: At least 1 question is required.[/red]")
        sys.exit(1)

    console.print()
    console.print(f"[green]Total questions collected: {len(questions)}[/green]")
    console.print()
    return questions


def get_installed_models() -> list[dict]:
    """Fetch locally installed Ollama models."""
    try:
        response = ollama.list()
        models = []
        for m in response.models:
            size_bytes = getattr(m, "size", 0) or 0
            size_gb = size_bytes / (1024 ** 3)
            modified = getattr(m, "modified_at", None)
            if modified and hasattr(modified, "strftime"):
                modified_str = modified.strftime("%Y-%m-%d %H:%M")
            elif modified:
                modified_str = str(modified)
            else:
                modified_str = "N/A"
            models.append({
                "name": m.model,
                "size": f"{size_gb:.1f} GB" if size_gb >= 1 else f"{size_bytes / (1024**2):.0f} MB",
                "modified": modified_str,
            })
        return models
    except Exception as e:
        console.print(f"[red]Error listing models: {e}[/red]")
        console.print("[red]Make sure Ollama is running (ollama serve).[/red]")
        sys.exit(1)


def display_models_table(models: list[dict]) -> None:
    """Display models in a rich table."""
    table = Table(
        title="[bold cyan]Available Ollama Models[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("#", style="bold white", justify="right", width=4)
    table.add_column("Model Name", style="green")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Modified", style="dim")

    for i, m in enumerate(models, 1):
        table.add_row(str(i), m["name"], m["size"], m["modified"])

    console.print(table)
    console.print()


def pull_model(model_cmd: str) -> str | None:
    """Pull a model from an ollama run command string."""
    parts = model_cmd.strip().split()
    # Accept "ollama run <model>" or just "<model>"
    if len(parts) >= 3 and parts[0] == "ollama" and parts[1] == "run":
        model_name = parts[2]
    elif len(parts) == 1:
        model_name = parts[0]
    else:
        console.print(f"[red]Invalid command format: {model_cmd}[/red]")
        return None

    console.print(f"[yellow]Pulling model '{model_name}'... This may take a while.[/yellow]")
    try:
        current_digest = ""
        for progress_response in ollama.pull(model_name, stream=True):
            digest = progress_response.get("digest", "")
            status = progress_response.get("status", "")
            if digest != current_digest:
                current_digest = digest
                console.print(f"  [dim]{status}[/dim]")
            elif status:
                total = progress_response.get("total", 0)
                completed = progress_response.get("completed", 0)
                if total > 0:
                    pct = completed / total * 100
                    console.print(f"  [dim]{status}: {pct:.0f}%[/dim]", end="\r")

        console.print(f"\n[green]Successfully pulled '{model_name}'.[/green]")
        return model_name
    except Exception as e:
        console.print(f"[red]Error pulling model: {e}[/red]")
        return None


def select_models(models: list[dict]) -> list[str]:
    """Let the user select models by number and optionally pull new ones."""
    display_models_table(models)

    while True:
        console.print("[cyan]Select models by entering comma-separated numbers.[/cyan]")
        console.print("[dim]Or type 'pull' to add a model not in the list.[/dim]")
        selection = console.input("  [bold]> [/bold]").strip()

        if not selection:
            console.print("[red]No selection made. Please try again.[/red]")
            continue

        if selection.lower() == "pull":
            cmd = console.input("  [cyan]Enter ollama run command (e.g. ollama run llama3): [/cyan]").strip()
            pulled = pull_model(cmd)
            if pulled:
                models.append({"name": pulled, "size": "N/A", "modified": "just now"})
                display_models_table(models)
            continue

        try:
            indices = [int(x.strip()) for x in selection.split(",")]
        except ValueError:
            console.print("[red]Invalid input. Enter numbers separated by commas.[/red]")
            continue

        invalid = [i for i in indices if i < 1 or i > len(models)]
        if invalid:
            console.print(f"[red]Invalid model number(s): {invalid}. Choose 1-{len(models)}.[/red]")
            continue

        selected = [models[i - 1]["name"] for i in indices]
        break

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for name in selected:
        if name not in seen:
            seen.add(name)
            unique.append(name)
    selected = unique

    if len(selected) > 3:
        console.print(
            "\n[bold yellow]Warning: You selected more than 3 models. "
            "The test may take a long time. Continue? (y/n)[/bold yellow]"
        )
        answer = console.input("  [bold]> [/bold]").strip().lower()
        if answer != "y":
            console.print("[yellow]Aborted by user.[/yellow]")
            sys.exit(0)

    console.print()
    console.print("[green]Selected models:[/green]")
    for name in selected:
        console.print(f"  [green]- {name}[/green]")
    console.print()
    return selected


def get_output_directory() -> str:
    """Ask the user for an output directory."""
    console.print("[cyan]Output directory for results (default: ./lm-arena-results):[/cyan]")
    path = console.input("  [bold]> [/bold]").strip()
    if not path:
        path = "./lm-arena-results"

    os.makedirs(path, exist_ok=True)
    console.print(f"[green]Output directory: {os.path.abspath(path)}[/green]\n")
    return path


def ensure_model_loaded(model_name: str) -> bool:
    """Ensure a model is loaded/available by attempting a trivial request."""
    try:
        ollama.chat(model=model_name, messages=[{"role": "user", "content": "hi"}])
        return True
    except Exception as e:
        console.print(f"[red]Error loading model '{model_name}': {e}[/red]")
        return False


def run_tests(
    models: list[str], questions: list[str], output_dir: str
) -> dict:
    """Run all questions against all models and collect results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results: dict = {}  # model_name -> {responses: [...], times: [...], file: str}

    total_tasks = len(models) * len(questions)
    completed = 0

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="green"),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        overall = progress.add_task("Overall Progress", total=total_tasks)

        for mi, model_name in enumerate(models, 1):
            console.print(
                Panel(
                    f"[bold cyan]Loading model: {model_name}[/bold cyan]",
                    border_style="cyan",
                )
            )

            # Try to load/warm up the model
            try:
                ollama.chat(
                    model=model_name,
                    messages=[{"role": "user", "content": "hello"}],
                )
            except Exception as e:
                console.print(
                    f"[bold red]Failed to load model '{model_name}': {e}. Skipping.[/bold red]"
                )
                # Advance progress for skipped questions
                for _ in questions:
                    completed += 1
                    progress.update(overall, completed=completed)
                continue

            results[model_name] = {"responses": [], "times": [], "file": ""}

            for qi, question in enumerate(questions, 1):
                progress.update(
                    overall,
                    description=f"[Model {mi}/{len(models)}: {model_name}] Q {qi}/{len(questions)}",
                )

                console.print(
                    f"  [cyan][Model: {model_name}] Question {qi}/{len(questions)} "
                    f"— generating response...[/cyan]"
                )

                start_time = time.time()
                try:
                    # Fresh session: only the current question in messages
                    full_response = ""
                    stream = ollama.chat(
                        model=model_name,
                        messages=[{"role": "user", "content": question}],
                        stream=True,
                    )

                    chunks = []
                    for chunk in stream:
                        token = chunk.message.content
                        chunks.append(token)

                    full_response = "".join(chunks)
                    elapsed = time.time() - start_time

                    results[model_name]["responses"].append(full_response)
                    results[model_name]["times"].append(elapsed)

                    # Show a preview panel
                    preview = full_response[:500]
                    if len(full_response) > 500:
                        preview += "\n[dim]... (truncated in preview)[/dim]"
                    console.print(
                        Panel(
                            preview,
                            title=f"[bold green]{model_name} — Q{qi}[/bold green]",
                            subtitle=f"[dim]{elapsed:.1f}s[/dim]",
                            border_style="green",
                            padding=(0, 1),
                        )
                    )

                except Exception as e:
                    elapsed = time.time() - start_time
                    error_msg = f"Error: {e}"
                    results[model_name]["responses"].append(error_msg)
                    results[model_name]["times"].append(elapsed)
                    console.print(f"    [red]{error_msg}[/red]")

                completed += 1
                progress.update(overall, completed=completed)

            # Write the per-model markdown file
            safe_name = model_name.replace(":", "_").replace("/", "_")
            filename = f"{safe_name}_{timestamp}.md"
            filepath = os.path.join(output_dir, filename)
            results[model_name]["file"] = filepath

            write_model_markdown(
                filepath, model_name, questions, results[model_name]
            )
            console.print(
                f"  [green]Results saved to: {filepath}[/green]\n"
            )

    # Write summary
    summary_file = os.path.join(output_dir, f"summary_{timestamp}.md")
    write_summary_markdown(summary_file, models, questions, results)

    return results


def write_model_markdown(
    filepath: str,
    model_name: str,
    questions: list[str],
    data: dict,
) -> None:
    """Write a per-model results markdown file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Model: {model_name}",
        f"**Test Date:** {now}",
        f"**Total Questions:** {len(questions)}",
        "",
        "---",
        "",
    ]

    for i, (q, a) in enumerate(zip(questions, data["responses"]), 1):
        elapsed = data["times"][i - 1]
        lines.extend([
            f"## Question {i}",
            f"**Q:** {q}",
            "",
            f"**A:**",
            a,
            "",
            f"*Response time: {elapsed:.1f}s*",
            "",
            "---",
            "",
        ])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_summary_markdown(
    filepath: str,
    models: list[str],
    questions: list[str],
    results: dict,
) -> None:
    """Write a summary markdown file with side-by-side comparisons."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Test Summary",
        f"**Date:** {now}",
        f"**Total Questions:** {len(questions)}",
        "",
        "## Tested Models",
        "",
    ]

    for model_name in models:
        if model_name in results:
            avg_time = (
                sum(results[model_name]["times"]) / len(results[model_name]["times"])
                if results[model_name]["times"]
                else 0
            )
            lines.append(f"- **{model_name}** — Avg response time: {avg_time:.1f}s")
        else:
            lines.append(f"- **{model_name}** — Skipped (failed to load)")

    lines.extend(["", "---", ""])

    # Side-by-side comparison
    lines.append("## Side-by-Side Comparison")
    lines.append("")

    for qi, question in enumerate(questions, 1):
        lines.append(f"### Question {qi}")
        lines.append(f"**Q:** {question}")
        lines.append("")

        for model_name in models:
            if model_name not in results:
                continue
            response = results[model_name]["responses"][qi - 1]
            elapsed = results[model_name]["times"][qi - 1]
            lines.append(f"#### {model_name} ({elapsed:.1f}s)")
            lines.append("")
            lines.append(response)
            lines.append("")

        lines.extend(["---", ""])

    # Average response time table
    lines.append("## Average Response Times")
    lines.append("")
    lines.append("| Model | Avg Response Time |")
    lines.append("|-------|-------------------|")
    for model_name in models:
        if model_name in results and results[model_name]["times"]:
            avg = sum(results[model_name]["times"]) / len(results[model_name]["times"])
            lines.append(f"| {model_name} | {avg:.1f}s |")
        else:
            lines.append(f"| {model_name} | N/A (skipped) |")

    lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def show_results_table(models: list[str], questions: list[str], results: dict) -> None:
    """Display a rich summary table in the terminal."""
    table = Table(
        title="[bold cyan]Test Results Summary[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("Model Name", style="green")
    table.add_column("Questions Answered", style="white", justify="center")
    table.add_column("Avg Response Time", style="yellow", justify="right")
    table.add_column("Output File", style="dim")

    for model_name in models:
        if model_name in results:
            data = results[model_name]
            answered = len(data["responses"])
            avg_time = (
                f"{sum(data['times']) / len(data['times']):.1f}s"
                if data["times"]
                else "N/A"
            )
            filepath = os.path.basename(data["file"])
        else:
            answered = 0
            avg_time = "N/A"
            filepath = "[red]Skipped[/red]"

        table.add_row(model_name, str(answered), avg_time, filepath)

    console.print()
    console.print(table)
    console.print()


def main():
    """Main entry point."""
    show_welcome()

    # Step 1: Collect questions
    questions = collect_questions()

    # Step 2: List and select models
    models_info = get_installed_models()
    if not models_info:
        console.print("[red]No models found. Install models with 'ollama pull <model>'.[/red]")
        sys.exit(1)

    selected_models = select_models(models_info)
    if not selected_models:
        console.print("[red]No models selected. Exiting.[/red]")
        sys.exit(1)

    # Step 3: Output directory
    output_dir = get_output_directory()

    # Step 4: Run tests
    console.print(
        Panel(
            f"[bold cyan]Starting tests: {len(selected_models)} model(s) x "
            f"{len(questions)} question(s)[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    results = run_tests(selected_models, questions, output_dir)

    # Step 5: Show summary
    show_results_table(selected_models, questions, results)

    # Find summary file
    summary_files = [f for f in os.listdir(output_dir) if f.startswith("summary_")]
    if summary_files:
        latest = sorted(summary_files)[-1]
        console.print(
            f"[green]Summary report saved to: "
            f"{os.path.join(output_dir, latest)}[/green]"
        )

    console.print("[bold green]All tests complete![/bold green]\n")


if __name__ == "__main__":
    main()
