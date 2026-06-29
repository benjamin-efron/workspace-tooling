# workspace-tooling

Portable workspace configuration. Each top-level directory is a workflow utility. Within each:

- `install.py` — idempotent setup script, run once per device
- `config/` — config files the tool reads at runtime
- `internal/` — scripts the tool calls at runtime (not user-facing)
- Any other `.py` files at the top level are user-facing scripts for that tool

No shell scripts. Python only, using stdlib exclusively (no global packages).

## Adding a new tool

1. Create a directory named after the tool.
2. Add `install.py` that symlinks `config/` and `internal/` contents to their expected OS locations.
3. Add `config/` and/or `internal/` as needed.

## aerospace

`install.py` creates:
- `~/.config/aerospace/aerospace.toml` → `aerospace/config/aerospace.toml`
- `~/.config/aerospace/internal/` → `aerospace/internal/`

The toml references scripts via `$HOME/.config/aerospace/internal/`, which resolves through
the symlink to this repo. This keeps the toml portable regardless of checkout path.
