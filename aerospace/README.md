# aerospace

Tiling window manager. Owns all keybindings, workspace-to-monitor layout, and window
rules. `aerospace.toml`'s `on-focus-changed` and `exec-on-workspace-change` hooks shell
out to Python scripts in `_mine/scripts/`, which in turn call Hammerspoon (`hs -c`) for
visual feedback.

## Depends on

- **[Hammerspoon](../hammerspoon/README.md)** — `focus-changed.py`, `monitor-switch.py`,
  and `workspace-changed.py` all call `hs -c "..."` to trigger window-flash, monitor
  mouse-warp, and workspace-badge feedback. AeroSpace itself installs and runs fine
  without Hammerspoon, but these callbacks silently no-op (`hs -c` errors, swallowed)
  until Hammerspoon is installed and its modules are loaded — see
  [hammerspoon/README.md](../hammerspoon/README.md) for the `init.lua` setup step.

No dependency the other direction: nothing in this repo requires AeroSpace to already
be running in order to install itself.

## Install

```sh
python3 aerospace/install.py
aerospace reload-config
```

Install [Hammerspoon](../hammerspoon/README.md) first if you want focus feedback
(border flash, workspace badge, mouse warp) working immediately after this step.

### Prerequisite

```sh
brew install --cask nikitabobko/tap/aerospace
```

### Required macOS settings

These must be configured manually before AeroSpace works correctly. Most are in
**System Settings → Desktop & Dock → Mission Control**.

#### Desktop & Dock

| Setting | Value | Notes |
|---------|-------|-------|
| Displays have separate Spaces | **OFF** | Required for AeroSpace to manage windows across monitors. Anchors the Dock to one display as a side effect. |
| Automatically rearrange Spaces based on most recent use | **OFF** | Keeps Space order stable. |
| When switching to an application, switch to a Space with open windows | **OFF** | Prevents macOS from hijacking workspace jumps. |
| Group windows by application | **ON** | AeroSpace recommendation — prevents parked windows from rendering tiny in Mission Control. |
| Automatically hide and show the Dock | **OFF** | |

#### Mission Control

Remove all extra native Spaces — AeroSpace replaces them. Leave just one.

#### Displays

- **Arrange**: Ensure each monitor has a free corner at the bottom so AeroSpace has
  somewhere to park hidden windows.
- **Main display**: Set your preferred monitor as Main so the Dock and menu bar live
  where you want them.

#### Privacy & Security → Accessibility

Grant AeroSpace Accessibility permission, then **relaunch the app** — the permission
only takes effect after a restart.

## Layout

- Workspaces `q w e r t` are force-assigned to monitor 1, `a s d f g` to monitor 2
  (`[workspace-to-monitor-force-assignment]` in `aerospace.toml`).
- All bindings live under the `cmd-alt` prefix — see `aerospace.toml` for the full list
  (window focus/move/resize, workspace jump/cycle/send-to, layout, monitor switch,
  fullscreen).

## Scripts (`_mine/scripts/`)

| Script | Triggered by | Does |
|--------|--------------|------|
| `focus-changed.py` | `on-focus-changed` | Calls `WindowFlash.show()` (Hammerspoon) to flash a border around the newly focused window. |
| `workspace-changed.py` | `exec-on-workspace-change` | Calls `WorkspaceIndicator.show(workspace)` for the on-screen badge, then `MonitorSwitch.onFocus(monitor)` to warp the mouse onto the newly focused monitor (skipped if the mouse is already there — see `hammerspoon/README.md`). |
| `monitor-switch.py` | `cmd-ctrl-alt-shift-w` binding, after `focus-monitor --wrap-around next` | Resolves the now-focused monitor name and calls `MonitorSwitch.onFocus`. |
| `workspace-cycle.py` | `cmd-alt-left` / `cmd-alt-right` bindings | Cycles to the next/previous workspace on the focused monitor only, given the workspace order passed as CLI args from `aerospace.toml`. |

## Common commands

```sh
aerospace reload-config              # reload aerospace.toml after editing (or re-running install.py)
aerospace list-workspaces --focused  # current workspace
aerospace list-monitors --focused    # current monitor
aerospace list-windows --all --json  # every window, across all workspaces, as JSON
aerospace flatten-workspace-tree     # fix a tiling layout that's gotten tangled
```
