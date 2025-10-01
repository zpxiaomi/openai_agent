# OpenAI Agent

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.

## Install uv

### macOS & Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
This script downloads the latest uv release and copies the binary to `~/.local/bin`. Make sure this directory is on your `PATH` (e.g. add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile).

### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
By default the installer places `uv.exe` in `%USERPROFILE%\.local\bin`. Confirm that folder is included in your `Path` environment variable.

## Project Setup

1. Ensure the desired Python version is available:
   ```bash
   uv python install 3.13
   ```
2. Sync dependencies and create the virtual environment:
   ```bash
   uv sync
   ```
   This creates a `.venv` directory with all locked dependencies.
3. Activate the environment (optional; uv commands auto-activate):
   ```bash
   source .venv/bin/activate     # macOS & Linux
   .venv\\Scripts\\Activate.ps1  # Windows PowerShell
   ```

## Common Tasks

- Run the project:
  ```bash
  uv run python -m openai_agent
  ```
- Add a new dependency:
  ```bash
  uv add <package>
  ```
- Run tests:
  ```bash
  uv run pytest
  ```

Consult the [uv documentation](https://docs.astral.sh/uv/) for advanced usage such as caching, multi-interpreter workflows, and CI integration.
