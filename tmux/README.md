# tmux

Standard tmux config: vim-style pane navigation/resizing, mouse support, vi copy mode,
and TPM-managed plugins. No path substitution is needed at install time — `tmux.conf`
has no machine-specific values.

## Depends on

Nothing in this repo. This is the only tool that other tools optionally depend on:

- **[claude](../claude/README.md)** — `notify.py` matches the tmux session name
  (`set-titles-string '#S'`, set in `tmux.conf`) against AeroSpace's window list to
  resolve which window/workspace hosts a given Claude Code session. Without
  `set -g set-titles on` from this config, that resolution silently fails and
  notifications fall back to "current focused workspace," which is usually wrong.
  Install tmux (and reload it — `set-titles` only takes effect after
  `tmux source ~/.tmux.conf` in existing sessions) before relying on notification
  navigation.

## Install

```sh
python3 tmux/install.py
tmux source ~/.tmux.conf   # reload config in any already-running tmux server
```

### Prerequisite

```sh
brew install tmux
```

### One-time manual step

Bootstrap TPM (Tmux Plugin Manager) if not already installed:

```sh
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
tmux source ~/.tmux.conf
```
Then press `prefix + I` inside tmux to install plugins (`tmux-resurrect`).

## Config highlights (`_mine/tmux.conf`)

- **Pane navigation**: `prefix h/j/k/l` to move, `prefix H/J/K/L` to resize by 5 cells.
- **Mouse**: enabled (`set -g mouse on`).
- **Window titles**: `set-titles on` / `set-titles-string '#S'` — makes the terminal
  window title track the tmux session name. Required for the `claude` hooks to resolve
  which AeroSpace window a session belongs to (see above).
- **Copy mode**: vi-style (`mode-keys vi`); `v` to start selection, `y` to copy to
  `pbcopy`.
- **Pane borders**: active pane highlighted in orange, top border shows pane index +
  title. Inactive panes are dimmed via `window-style`.
- **New panes/windows** (`"`, `%`, `c`) open in the current pane's working directory.

## Common commands

```sh
tmux source ~/.tmux.conf   # reload config
prefix + I                 # install/update TPM plugins
prefix + h/j/k/l           # move between panes
prefix + H/J/K/L           # resize the focused pane
```
