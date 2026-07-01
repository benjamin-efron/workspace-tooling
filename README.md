# workspace-tooling

Portable macOS workspace configuration: window management, terminal multiplexing, and
editor-integration glue, kept in one repo and pushed out to each tool's expected config
location by a per-tool `install.py`.

The repo is the **source of truth**. Installed config files are generated artifacts —
never edit them directly, edit the source in this repo and re-run the relevant
`install.py`.

## Tools

| Tool | Purpose | Docs |
|------|---------|------|
| [AeroSpace](https://github.com/nikitabobko/AeroSpace) | Tiling window manager — keybindings, workspace-to-monitor layout, window rules | [aerospace/README.md](aerospace/README.md) |
| [Hammerspoon](https://www.hammerspoon.org) | macOS automation — visual feedback (window flash, workspace badge, monitor mouse-warp) and the Claude Code notification HUD | [hammerspoon/README.md](hammerspoon/README.md) |
| [tmux](https://github.com/tmux/tmux) | Terminal multiplexer — vim-style navigation/resizing, TPM plugin management | [tmux/README.md](tmux/README.md) |
| [Claude Code](https://claude.com/claude-code) | Stop/Notification hooks — resolves which AeroSpace window/workspace a Claude session is running in and hands it to Hammerspoon | [claude/README.md](claude/README.md) |

Each subdirectory README covers that tool in depth: what it depends on, how to install
it, and the commands you'll reach for day to day. This file stays focused on the repo
as a whole.

## Project structure

Each top-level directory is a self-contained tool:

```
<tool>/
  install.py          # idempotent setup script
  _mine/               # everything the tool needs at runtime
    config/            # config files (if the tool needs a separate config location)
    scripts/           # scripts invoked by the tool at runtime
```

Not every tool needs both `config/` and `scripts/` under `_mine/` — use whatever
structure fits. The `_mine/` name marks the directory as fully owned and replaced by
`install.py`; nothing outside it should be written there by hand.

## Design principles

- **Copy-based installs, not symlinks.** Each `install.py` fully replaces its target
  (`rmtree` + `copytree` for directories, overwrite for files). This is simple,
  predictable, and avoids dangling symlinks. The tradeoff: edits must be made in the
  repo and re-installed — never edit installed files directly.

- **All configuration lives in the repo.** Runtime scripts are generic and take
  configuration as arguments rather than hardcoding values, so they work unmodified on
  any machine. For example, workspace order is defined once in `aerospace.toml` and
  passed as CLI args to `workspace-cycle.py`.

- **Install-time path expansion.** Some tools (e.g. AeroSpace) launch as GUI apps
  without a shell environment, so env vars like `$HOME` never get expanded at runtime.
  `install.py` substitutes absolute paths into config files before writing them. Source
  files in the repo use `$HOME` as a readable placeholder.

- **Python only, stdlib only.** No shell scripts, no global packages. Every
  `install.py` and every runtime script invoked by a tool (e.g. an AeroSpace
  exec-and-forget callback) is plain Python using only the standard library.

- **Prerequisite checks.** Each `install.py` checks that the required binary or app is
  present and prints install instructions if it's missing, rather than failing
  silently partway through.

- **One-time manual steps are printed, not automated.** When a tool needs a one-time
  per-machine action that can't be scripted safely (e.g. appending a snippet to an
  unmanaged config file like `~/.hammerspoon/init.lua`), `install.py` prints clear
  instructions instead of modifying a file it doesn't own.

- **Minimize Hammerspoon.** Hammerspoon is the least reliable piece of this stack —
  prefer the `aerospace` CLI and Python for control flow (focus switching, workspace
  navigation, monitor targeting). Reserve Hammerspoon/Lua for drawing on-screen UI
  (canvases, overlays) and anything only it can do. When Hammerspoon must trigger a
  focus/workspace change, shell out to `aerospace` (via `hs.task.new`) rather than
  using Hammerspoon's own window/screen APIs (e.g. `hs.window():focus()`) — mixing the
  two causes AeroSpace's internal state to fall out of sync with macOS's actual focus,
  producing flicker/revert bugs. AeroSpace should be the single source of truth for
  focus and workspace state.

## Setup on a new machine

Install order matters: Hammerspoon must be installed before Claude Code (the Claude
hook writes notifications that Hammerspoon reads), and AeroSpace's own scripts call out
to Hammerspoon, so install AeroSpace after Hammerspoon too.

```sh
git clone https://github.com/benjamin-efron/workspace-tooling
cd workspace-tooling

python3 hammerspoon/install.py
# Follow the printed instructions to update ~/.hammerspoon/init.lua, then reload Hammerspoon

python3 aerospace/install.py
aerospace reload-config

python3 tmux/install.py
# Run: tmux source ~/.tmux.conf

python3 claude/install.py
# Follow the printed instructions to add hooks to ~/.claude/settings.json
```

See each tool's README for prerequisites, required macOS settings, and common commands.

## Adding a new tool

1. Create a directory named after the tool.
2. Add `install.py`:
   - Check prerequisites with a clear error message if missing.
   - Copy config files to their OS-expected locations, substituting `$HOME` with
     `str(Path.home())` if the tool doesn't expand env vars at runtime.
   - Fully replace any managed directories: `shutil.rmtree(dst)` then
     `shutil.copytree(src, dst)`.
   - Print any one-time manual steps the user needs to take.
3. Add `_mine/` with the tool's config and/or scripts.
4. Add a README.md for the tool (dependencies, install steps, common commands).
5. Add the tool to the table and install order above.
