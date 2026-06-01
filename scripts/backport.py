#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "questionary",
#   "rich",
#   "pyyaml",
# ]
# ///
"""Interactive backport tool: pick a changed file, review the diff, apply it."""

import re
import sys
import argparse
import difflib
import subprocess
from pathlib import Path

import yaml
import questionary
from rich.console import Console
from rich.text import Text
from rich.rule import Rule

ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = ROOT / "template"
APP_DIR = ROOT / "app"
COPIER_ANSWERS = APP_DIR / ".copier-answers.yml"
SKIP_FILES = {".copier-answers.yml"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".mypy_cache", ".ruff_cache", ".pytest_cache"}

console = Console()


def load_vars() -> dict[str, str]:
    if not COPIER_ANSWERS.exists():
        console.print(f"[red]Missing {COPIER_ANSWERS}[/red]")
        sys.exit(1)
    data = yaml.safe_load(COPIER_ANSWERS.read_text())
    return {
        "project_name": data["project_name"],
        "project_slug": data["project_slug"],
        "python_package_name": data["python_package_name"],
        "description": data["description"],
        "github_username": data["github_username"],
    }


def make_render(vars: dict[str, str]):
    """Return a function that substitutes [[ var ]] → value."""
    def render(text: str) -> str:
        for key, value in vars.items():
            text = text.replace(f"[[ {key} ]]", value)
        return text
    return render


def make_derender(vars: dict[str, str]):
    """Return a function that substitutes value → [[ var ]].
    Ordered longest-value-first to avoid partial matches.
    """
    pairs = sorted(vars.items(), key=lambda kv: len(kv[1]), reverse=True)
    def derender(text: str) -> str:
        for key, value in pairs:
            text = text.replace(value, f"[[ {key} ]]")
        return text
    return derender


def read_text_safe(path: Path) -> str | None:
    """Return file text, or None if it's binary."""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def find_changed(render) -> list[str]:
    changed = []
    for tpl in sorted(TEMPLATE_DIR.rglob("*")):
        if not tpl.is_file():
            continue
        rel = tpl.relative_to(TEMPLATE_DIR)
        if str(rel) in SKIP_FILES:
            continue
        app = APP_DIR / rel
        if not app.exists():
            continue
        tpl_text = read_text_safe(tpl)
        app_text = read_text_safe(app)
        if tpl_text is None or app_text is None:
            continue
        if render(tpl_text) != app_text:
            changed.append(str(rel))
    return changed


def get_gitignored(app_dir: Path, rel_paths: list[str]) -> set[str]:
    if not rel_paths:
        return set()
    try:
        result = subprocess.run(
            ["git", "-C", str(app_dir), "check-ignore", "-z", "--stdin"],
            input="\0".join(rel_paths),
            capture_output=True,
            text=True,
        )
        return set(filter(None, result.stdout.split("\0")))
    except (FileNotFoundError, subprocess.SubprocessError):
        return set()


def find_new() -> list[str]:
    candidates = []
    for app_file in sorted(APP_DIR.rglob("*")):
        if not app_file.is_file():
            continue
        if any(part in SKIP_DIRS for part in app_file.relative_to(APP_DIR).parts):
            continue
        rel = app_file.relative_to(APP_DIR)
        if str(rel) in SKIP_FILES:
            continue
        if not (TEMPLATE_DIR / rel).exists():
            candidates.append(str(rel))
    ignored = get_gitignored(APP_DIR, candidates)
    return [r for r in candidates if r not in ignored]


def find_deleted() -> list[str]:
    deleted = []
    for tpl in sorted(TEMPLATE_DIR.rglob("*")):
        if not tpl.is_file():
            continue
        rel = tpl.relative_to(TEMPLATE_DIR)
        if str(rel) in SKIP_FILES:
            continue
        if not (APP_DIR / rel).exists():
            deleted.append(str(rel))
    return deleted


def show_diff(tpl_rendered: str, app_text: str, rel: str) -> None:
    diff = list(difflib.unified_diff(
        tpl_rendered.splitlines(keepends=True),
        app_text.splitlines(keepends=True),
        fromfile=f"template/{rel}",
        tofile=f"app/{rel}",
    ))
    if not diff:
        console.print("[yellow]Files are identical.[/yellow]")
        return

    text = Text()
    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            text.append(line, style="bold")
        elif line.startswith("+"):
            text.append(line, style="green")
        elif line.startswith("-"):
            text.append(line, style="red")
        elif line.startswith("@@"):
            text.append(line, style="cyan")
        else:
            text.append(line)
    console.print(text)


def backport(rel: str, derender) -> None:
    app = APP_DIR / rel
    tpl = TEMPLATE_DIR / rel
    tpl.parent.mkdir(parents=True, exist_ok=True)
    tpl.write_text(derender(app.read_text(encoding="utf-8")), encoding="utf-8")
    console.print(f"[green]Backported:[/green] {rel}")


def delete_from_template(rel: str) -> None:
    tpl = TEMPLATE_DIR / rel
    tpl.unlink()
    console.print(f"[red]Deleted from template:[/red] {rel}")


_DEL_PREFIX = "[deleted] "
_NEW_PREFIX = "[new] "


def main() -> None:
    global APP_DIR, COPIER_ANSWERS

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app-dir",
        type=Path,
        default=APP_DIR,
        help=f"Path to the app directory (default: {APP_DIR})",
    )
    args = parser.parse_args()
    APP_DIR = args.app_dir.resolve()
    COPIER_ANSWERS = APP_DIR / ".copier-answers.yml"

    vars = load_vars()
    render = make_render(vars)
    derender = make_derender(vars)

    while True:
        changed = find_changed(render)
        deleted = find_deleted()
        new = find_new()

        if not changed and not deleted and not new:
            console.print("[green]No changed, deleted, or new files.[/green]")
            break

        choices: list = []
        if changed:
            choices.append(questionary.Separator("── changed ──"))
            choices.extend(changed)
        if deleted:
            choices.append(questionary.Separator("── deleted in app ──"))
            choices.extend(f"{_DEL_PREFIX}{r}" for r in deleted)
        if new:
            choices.append(questionary.Separator("── new in app ──"))
            choices.extend(f"{_NEW_PREFIX}{r}" for r in new)
        choices.extend([questionary.Separator(), "quit"])

        console.print(Rule("Backport tool"))
        selection = questionary.select(
            "Which file to backport?",
            choices=choices,
        ).ask()

        if selection is None or selection == "quit":
            break

        if selection.startswith(_DEL_PREFIX):
            rel = selection[len(_DEL_PREFIX):]
            console.print()
            console.print(Rule(rel))
            console.print(f"[red]File deleted from app — will remove from template:[/red] {rel}")
            console.print()
            if questionary.confirm("Delete this file from template?", default=False).ask():
                delete_from_template(rel)
            else:
                console.print("[yellow]Skipped.[/yellow]")
        elif selection.startswith(_NEW_PREFIX):
            rel = selection[len(_NEW_PREFIX):]
            app = APP_DIR / rel
            app_text = read_text_safe(app) or ""
            console.print()
            console.print(Rule(rel))
            show_diff("", app_text, rel)
            console.print()
            if questionary.confirm("Add this file to template?", default=False).ask():
                backport(rel, derender)
            else:
                console.print("[yellow]Skipped.[/yellow]")
        else:
            rel = selection
            tpl = TEMPLATE_DIR / rel
            app = APP_DIR / rel
            tpl_rendered = render(read_text_safe(tpl) or "")
            app_text = read_text_safe(app) or ""

            console.print()
            console.print(Rule(rel))
            show_diff(tpl_rendered, app_text, rel)
            console.print()

            if questionary.confirm("Apply this backport?", default=False).ask():
                backport(rel, derender)
            else:
                console.print("[yellow]Skipped.[/yellow]")

        console.print()
        if not questionary.confirm("Continue with another file?", default=True).ask():
            break


if __name__ == "__main__":
    main()
