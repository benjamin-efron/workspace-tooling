# claude

Claude Code hooks that fire on every `Notification` and `Stop` event, resolve which
AeroSpace window/workspace and tmux session the event came from, and hand that off to
Hammerspoon's notification HUD.

## Depends on

- **[hammerspoon](../hammerspoon/README.md)** — `notify.py` writes a JSON file to
  `~/.hammerspoon/notifications/<session_id>.json`; Hammerspoon's `claude_notifications`
  module (a `pathwatcher`) picks it up and renders the HUD. Without Hammerspoon
  installed and `ClaudeNotifications = require('claude_notifications')` in `init.lua`,
  notification files are written but never displayed or cleaned up.
- **[aerospace](../aerospace/README.md)** — `notify.py` calls the `aerospace` CLI
  (`list-windows --all --json`, `list-workspaces --focused`) to resolve the session's
  window/workspace and to suppress notifications when the user is already looking at
  the session.
- **[tmux](../tmux/README.md)** — `notify.py` reads `TMUX_PANE` and calls `tmux
  display-message` to get the session name and pane-active state. Window/workspace
  resolution additionally depends on tmux's `set-titles-string '#S'` (see
  [tmux/README.md](../tmux/README.md)) to make the terminal window title match the
  tmux session name — without it, resolution silently fails and every notification
  falls back to "current focused workspace."

Install order: hammerspoon → aerospace → tmux → claude, so every dependency this hook
relies on is already in place before it's wired up. See the
[root README](../README.md#setup-on-a-new-machine) for the full sequence.

## Install

```sh
python3 claude/install.py
```
Follow the printed instructions to add the `Notification`/`Stop` hook entries to
`~/.claude/settings.json` (never modified directly, since it may hold other unrelated
settings) and to confirm `ClaudeNotifications = require('claude_notifications')` is in
`~/.hammerspoon/init.lua`.

## How it works (`_mine/hooks/notify.py`)

1. Reads the hook payload from stdin for `session_id`; reads `TMUX_PANE` from the
   environment.
2. Resolves a human-readable `label` via `tmux display-message -p '#S:#I (#W)'`,
   falling back to the current directory name.
3. **Resolves the session's real window/workspace** (`_resolve_window()`): gets the
   tmux session name for `TMUX_PANE`, then matches it against
   `aerospace list-windows --all --json` for a Ghostty window whose title equals that
   session name. This relies on tmux's `set-titles-string '#S'` — Ghostty's AppleScript
   dictionary has no `tty` property, so there's no way to map a pty device straight to
   a window; matching on title is the workaround.
4. **Suppresses the notification** if the resolved workspace matches the currently
   focused AeroSpace workspace *and* tmux reports the pane as both the active window
   and active pane (`#{window_active}#{pane_active}` == `"11"`) — i.e. the user is
   already looking at the session. A failed resolution is never treated as a match.
5. Writes `~/.hammerspoon/notifications/<session_id short>.json` with the label,
   resolved workspace, tmux pane, and window-id.
6. Appends a debug line to `~/.claude/notify-debug.log` for every invocation
   (resolved/focused workspace, pane status, whether it suppressed) — useful for
   diagnosing resolution failures without adding print statements.

On the Hammerspoon side, selecting a notification in the HUD runs three phases, each
assuming the previous one succeeded regardless of whether it took any action:

1. `aerospace focus --window-id <id>` — focuses the exact window (pulls in the correct
   monitor and workspace as a side effect). Falls back to `aerospace workspace <ws>` if
   no window-id was resolved.
2. (fallback only) `aerospace workspace <ws>`.
3. `tmux switch-client -t <pane>`.

Phase 1 deliberately uses AeroSpace's own `focus` command rather than
`hs.window():focus()` or a redundant `aerospace workspace` call afterward — either
caused AeroSpace's internal state to desync from macOS's actual focus, producing a
flash-then-revert.

## Common commands

```sh
tail -f ~/.claude/notify-debug.log   # watch notification resolution in real time
hs -c "print(hs.console.getConsole())"  # Hammerspoon-side debug output (see hammerspoon/README.md)
```
