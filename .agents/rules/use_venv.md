# Rule: Use uv for Python

## Trigger
This rule applies whenever you run Python scripts or install Python packages.

## Action
`uv` is the only Python environment manager used in this project. Never call bare
`python` / `python3`, never call `pip`, and never create an environment with
`python3 -m venv`.

1. **Execution**: `uv run python scripts/<script>.py`. `uv run` resolves the
   project's `.venv` automatically from the repo root.
2. **Installation**: `uv pip install <package>` (and add the package to
   `requirements.txt`).
3. **Creation**: If `.venv` is missing, recreate it:
   `uv venv && uv pip install -r requirements.txt`.
4. **Ad-hoc tools**: For a one-off tool that does not belong in
   `requirements.txt`, use `uvx <tool>` rather than installing it into `.venv`.
