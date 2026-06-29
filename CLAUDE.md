# workspace-tooling

Portable macOS workspace configuration. Each top-level directory is a tool. The repo is the source of truth — `install.py` pushes config to OS-expected locations, not the other way around.

## Design principles

**Copy-based installs, not symlinks.** Each `install.py` fully replaces its target (rmtree + copytree for directories, overwrite for files). This is simple, predictable, and avoids dangling symlinks. The downside is that edits must be made in the repo and re-installed — never edit installed files directly.

**All configuration lives in the repo.** Runtime scripts should be generic and receive configuration as arguments rather than hardcoding values. For example, workspace order is defined in `aerospace.toml` and passed as CLI args to `workspace-cycle.py`, so the script works on any machine without modification.

**Install-time path expansion.** Some tools (e.g. AeroSpace) launch as GUI apps without a shell environment, so env vars like `$HOME` are not expanded at runtime. `install.py` handles this by substituting absolute paths into config files before writing them. Source files in the repo use `$HOME` as a readable placeholder.

**Python only, stdlib only.** No shell scripts. No global packages. `install.py` scripts run with system Python and use only the standard library. Runtime scripts called by tools (e.g. AeroSpace exec-and-forget scripts) follow the same rule.

**Prerequisite checks.** Each `install.py` checks that the required binary or app is present and prints install instructions if not, rather than failing silently.

**One-time manual steps are printed, not automated.** When a tool requires a one-time action per machine that can't be scripted safely (e.g. adding a snippet to an unmanaged config file), `install.py` prints clear instructions rather than modifying files it doesn't own.

## Directory structure

Each tool follows this layout:

```
<tool>/
  install.py          # idempotent setup script
  internal/           # everything the tool needs at runtime
    config/           # config files (if the tool needs a separate config location)
    scripts/          # scripts called by the tool at runtime
```

Not all tools need both `config/` and `scripts/` — use whatever structure makes sense. The `internal/` directory is fully replaced on each install.

## Adding a new tool

1. Create a directory named after the tool.
2. Add `install.py`:
   - Check prerequisites with a clear error message if missing.
   - Copy config files to their OS-expected locations, substituting `$HOME` with `str(Path.home())` if the tool doesn't expand env vars at runtime.
   - Fully replace any managed directories: `shutil.rmtree(dst)` then `shutil.copytree(src, dst)`.
   - Print any one-time manual steps the user needs to take.
3. Add `internal/` with the tool's config and/or scripts.
4. Add the tool to the README table.

## Tools

### aerospace

AeroSpace is a tiling WM that launches as a GUI app at login. Its `exec-and-forget` directive execs scripts directly without a shell, so env vars are not available. `install.py` substitutes `$HOME` with the absolute home path before writing `aerospace.toml`.

Runtime scripts in `aerospace/internal/scripts/` are called by AeroSpace bindings. They use full binary paths (`/opt/homebrew/bin/hs`, `/opt/homebrew/bin/aerospace`) since Homebrew's PATH is not available in AeroSpace's runtime environment.

### hammerspoon

Hammerspoon manages visual feedback triggered by AeroSpace events: window border flash on focus change, workspace badge on workspace switch, and mouse warp on monitor switch. `install.py` only manages `~/.hammerspoon/internal/` — it never touches `init.lua`, which varies per machine. Instead it prints a snippet for the user to add manually once.

### tmux

Standard tmux config. No path substitution needed. After install, run `tmux source ~/.tmux.conf`. Plugins are managed by TPM — if not yet installed, bootstrap instructions are printed by `install.py`.
