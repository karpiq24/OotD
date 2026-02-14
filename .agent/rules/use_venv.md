
# Rule: Use Local Virtual Environment

## Trigger
This rule applies whenever you run Python scripts or install Python packages.

## Action
1. **Prefer Local Venv**: Always look for a `.venv` directory in the project root.
2. **Execution**: Run python scripts using the venv interpreter: `.venv/bin/python` instead of just `python` or `python3`.
3. **Installation**: Install packages into the venv: `.venv/bin/pip install <package>`.
4. **Creation**: If a venv is missing but needed, ask the user or create it: `python3 -m venv .venv`.
