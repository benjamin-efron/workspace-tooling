# hammerspoon

macOS automation, used narrowly here for on-screen visual feedback and the Claude Code
notification HUD. Per the [root README's design principles](../README.md#design-principles),
Hammerspoon is intentionally minimized — control flow (focus switching, workspace
navigation, monitor targeting) is delegated to the `aerospace` CLI via `hs.task.new`
rather than Hammerspoon's own window/screen APIs, to keep AeroSpace as the single
source of truth for focus/workspace state.

## Depends on

- **`aerospace` CLI binary** (`/opt/homebrew/bin/aerospace`) — `claude_notifications.lua`
  shells out to it to focus windows/workspaces when a notification is selected. Not
  required at install time, only when that feature is used.
- **`tmux` CLI binary** (`/opt/homebrew/bin/tmux`) — same file, to switch the active
  tmux client/pane.
- **[claude](../claude/README.md)** — `claude_notifications.lua` watches
  `~/.hammerspoon/notifications/` for files written by `claude/_mine/hooks/notify.py`.
  Nothing breaks if the `claude` hooks aren't installed; the watcher just never sees
  any files.

Nothing in this repo requires Hammerspoon to be installed first — but install it before
[aerospace](../aerospace/README.md) if you want focus feedback (border flash, workspace
badge, mouse warp) working the moment AeroSpace starts firing its callbacks.

## Install

```sh
python3 hammerspoon/install.py
```

### Prerequisite

```sh
brew install --cask hammerspoon
```
Then enable CLI access: Hammerspoon menu → **Install CLI Tools** (needed for `hs -c ...`
and for `install.py`'s prerequisite check to pass via the `hs` binary).

### One-time manual step

`install.py` only manages `~/.hammerspoon/_mine/` — it never touches `init.lua`, since
that file varies per machine and may contain other unmanaged config. After installing,
add the snippet `install.py` prints to `~/.hammerspoon/init.lua`:

```lua
package.path = package.path .. ';' .. os.getenv('HOME') .. '/.hammerspoon/_mine/?.lua'
MonitorSwitch      = require('monitor_switch')
WorkspaceIndicator = require('workspace_indicator')
WindowFlash        = require('window_flash')
ClaudeNotifications = require('claude_notifications')
```

Then reload Hammerspoon (see below). Re-running `install.py` after editing a script
does **not** require re-adding this snippet — it's a one-time step per machine.

## Modules (`_mine/scripts/`)

| Module | Global | Called by | Does |
|--------|--------|-----------|------|
| `window_flash.lua` | `WindowFlash` | `aerospace/_mine/scripts/focus-changed.py` | Flashes a colored border around the focused window on every focus change (0.2s, 0.3s cooldown). |
| `workspace_indicator.lua` | `WorkspaceIndicator` | `aerospace/_mine/scripts/workspace-changed.py` | Shows a badge with the workspace letter on the focused screen for 0.5s. |
| `monitor_switch.lua` | `MonitorSwitch` | `aerospace/_mine/scripts/workspace-changed.py`, `monitor-switch.py` | Warps the mouse onto the newly focused monitor — skipped if the mouse is already there, so a mouse-driven monitor switch (e.g. clicking a window on the other monitor) doesn't yank the cursor away. |
| `claude_notifications.lua` | `ClaudeNotifications` | `hs.pathwatcher` on `~/.hammerspoon/notifications/` | Renders the notification HUD (Hyper-n to toggle) and, on selecting an entry, navigates via AeroSpace (`focus --window-id` → `workspace` fallback → tmux `switch-client`) — see [claude/README.md](../claude/README.md) for the full resolution flow. |

## Common commands

```sh
hs -c "hs.reload()"                        # reload config from the CLI (after install.py or a manual edit)
hs -c "print(hs.console.getConsole())"     # dump the Hammerspoon console (debug print() output)
hs -c "hs.openConsole()"                   # open the console window
```

Hyper-n (`cmd-ctrl-alt-shift-n`) toggles the Claude Code notification HUD.
