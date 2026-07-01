# workspace-tooling

Portable macOS workspace configuration. Each top-level directory is a tool. The repo is the source of truth — `install.py` pushes config to OS-expected locations, not the other way around.

## Design principles

**Copy-based installs, not symlinks.** Each `install.py` fully replaces its target (rmtree + copytree for directories, overwrite for files). This is simple, predictable, and avoids dangling symlinks. The downside is that edits must be made in the repo and re-installed — never edit installed files directly.

**All configuration lives in the repo.** Runtime scripts should be generic and receive configuration as arguments rather than hardcoding values. For example, workspace order is defined in `aerospace.toml` and passed as CLI args to `workspace-cycle.py`, so the script works on any machine without modification.

**Install-time path expansion.** Some tools (e.g. AeroSpace) launch as GUI apps without a shell environment, so env vars like `$HOME` are not expanded at runtime. `install.py` handles this by substituting absolute paths into config files before writing them. Source files in the repo use `$HOME` as a readable placeholder.

**Python only, stdlib only.** No shell scripts. No global packages. `install.py` scripts run with system Python and use only the standard library. Runtime scripts called by tools (e.g. AeroSpace exec-and-forget scripts) follow the same rule.

**Prerequisite checks.** Each `install.py` checks that the required binary or app is present and prints install instructions if not, rather than failing silently.

**One-time manual steps are printed, not automated.** When a tool requires a one-time action per machine that can't be scripted safely (e.g. adding a snippet to an unmanaged config file), `install.py` prints clear instructions rather than modifying files it doesn't own.

**Minimize Hammerspoon.** Hammerspoon is unreliable — prefer the `aerospace` CLI and Python for control flow (focus switching, workspace navigation, monitor targeting). Reserve Hammerspoon/Lua for drawing on-screen UI (canvases, overlays) and other tasks only it can do. When Hammerspoon must trigger a focus/workspace change, shell out to `aerospace` (via `hs.task.new`) rather than using Hammerspoon's own window/screen APIs (e.g. `hs.window():focus()`) — mixing the two causes AeroSpace's internal state to fall out of sync with macOS's actual focus, producing flicker/revert bugs. AeroSpace should be the single source of truth for focus and workspace state.

## Directory structure

Each tool follows this layout:

```
<tool>/
  install.py          # idempotent setup script
  _mine/           # everything the tool needs at runtime
    config/           # config files (if the tool needs a separate config location)
    scripts/          # scripts called by the tool at runtime
```

Not all tools need both `config/` and `scripts/` — use whatever structure makes sense. The `_mine/` directory is fully replaced on each install.

## Adding a new tool

1. Create a directory named after the tool.
2. Add `install.py`:
   - Check prerequisites with a clear error message if missing.
   - Copy config files to their OS-expected locations, substituting `$HOME` with `str(Path.home())` if the tool doesn't expand env vars at runtime.
   - Fully replace any managed directories: `shutil.rmtree(dst)` then `shutil.copytree(src, dst)`.
   - Print any one-time manual steps the user needs to take.
3. Add `_mine/` with the tool's config and/or scripts.
4. Add the tool to the root README's table and install order.
5. Add a per-tool `README.md`: dependencies on other tools in this repo, install steps
   and prerequisites, and common commands.

## Tools

### aerospace

AeroSpace is a tiling WM that launches as a GUI app at login. Its `exec-and-forget` directive execs scripts directly without a shell, so env vars are not available. `install.py` substitutes `$HOME` with the absolute home path before writing `aerospace.toml`.

Runtime scripts in `aerospace/_mine/scripts/` are called by AeroSpace bindings. They use full binary paths (`/opt/homebrew/bin/hs`, `/opt/homebrew/bin/aerospace`) since Homebrew's PATH is not available in AeroSpace's runtime environment.

### hammerspoon

Hammerspoon manages visual feedback triggered by AeroSpace events: window border flash on focus change, workspace badge on workspace switch, and mouse warp on monitor switch. `install.py` only manages `~/.hammerspoon/_mine/` — it never touches `init.lua`, which varies per machine. Instead it prints a snippet for the user to add manually once.

The monitor mouse-warp (`monitor_switch.lua`'s `MonitorSwitch.onFocus`) is skipped when `hs.mouse.getCurrentScreen()` already equals the target screen — this covers both a mouse-driven monitor switch (clicking a window on the other monitor) and a same-monitor keyboard workspace jump (where the mouse never left that screen to begin with), neither of which should yank the cursor to the corner.

### tmux

Standard tmux config. No path substitution needed. After install, run `tmux source ~/.tmux.conf`. Plugins are managed by TPM — if not yet installed, bootstrap instructions are printed by `install.py`.

### claude

Claude Code hooks that fire on every `Stop` and `Notification` event. `install.py` copies `_mine/` to `~/.claude/_mine/` and prints the JSON snippet to add to `~/.claude/settings.json` — it never touches that file directly since it contains other per-machine settings.

`notify.py` resolves which AeroSpace workspace and window the Claude session is on via:
1. `$TMUX_PANE` → tmux session name (`#{session_name}`)
2. `aerospace list-windows --all --json` to find the Ghostty window whose title equals the session name — this relies on `tmux.conf` setting `set-titles on` / `set-titles-string '#S'`, since Ghostty's AppleScript dictionary has no way to map a pty device to a window (no `tty` property exists on its `terminal` element, despite the name suggesting otherwise).

The resolved workspace, window-id, and tmux pane are written to `~/.hammerspoon/notifications/<session_id>.json`. Hammerspoon's pathwatcher picks this up and shows the notification HUD. On selection, `claude_notifications.lua` runs phases assuming the prior phase succeeded regardless of outcome: (1) `aerospace focus --window-id <id>` to pull the correct monitor and workspace into focus (falls back to `aerospace workspace <ws>` if no window-id was resolved), then (2) `tmux switch-client -t <pane>`. Focus is deliberately routed through AeroSpace's own commands rather than `hs.window():focus()` or a redundant `aerospace workspace` call after the window focus — either caused AeroSpace's internal state to desync from macOS's actual focus, producing a flash-then-revert.

`notify.py` also suppresses the notification file write entirely when the resolved workspace matches the currently-focused AeroSpace workspace and tmux reports the pane as both the active window and active pane (`#{window_active}#{pane_active}` == `"11"`) — i.e. the user is already looking at the session.
