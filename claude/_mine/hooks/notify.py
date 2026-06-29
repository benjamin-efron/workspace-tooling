#!/usr/bin/python3
"""Claude Code hook — writes a notification file for Hammerspoon's pathwatcher."""
import json
import os
import subprocess
import sys

AEROSPACE = '/opt/homebrew/bin/aerospace'
TMUX      = '/opt/homebrew/bin/tmux'

try:
    payload = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

session_id = payload.get('session_id', '').strip()
if not session_id:
    sys.exit(0)

tmux_pane = os.environ.get('TMUX_PANE', '')

label = ''
if tmux_pane:
    label = subprocess.run(
        [TMUX, 'display-message', '-t', tmux_pane, '-p', '#S:#I (#W)'],
        capture_output=True, text=True,
    ).stdout.strip()
if not label:
    label = os.path.basename(os.getcwd()) or session_id[:12]


def _ghostty_window_title_for_tty(tty):
    """Ask Ghostty which window contains the given tty device path."""
    script = (
        'tell application "Ghostty"\n'
        '    repeat with w in every window\n'
        '        repeat with t in every terminal of w\n'
        '            if tty of t is "' + tty + '" then\n'
        '                return name of w\n'
        '            end if\n'
        '        end repeat\n'
        '    end repeat\n'
        'end tell'
    )
    r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''


def _workspace_for_window_title(title):
    """Return the AeroSpace workspace containing a Ghostty window with the given title."""
    r = subprocess.run(
        [AEROSPACE, 'list-windows', '--workspace', 'all', '--json'],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    try:
        windows = json.loads(r.stdout)
    except Exception:
        return None
    for w in windows:
        if w.get('window-title', '') == title:
            return w.get('workspace')
    return None


def _resolve_workspace():
    if not tmux_pane:
        return None

    session = subprocess.run(
        [TMUX, 'display-message', '-t', tmux_pane, '-p', '#{session_name}'],
        capture_output=True, text=True,
    ).stdout.strip()
    if not session:
        return None

    clients = subprocess.run(
        [TMUX, 'list-clients', '-t', session, '-F', '#{client_tty}'],
        capture_output=True, text=True,
    ).stdout.strip().splitlines()

    for line in clients:
        tty = line.strip()
        if not tty:
            continue
        title = _ghostty_window_title_for_tty(tty)
        if title:
            ws = _workspace_for_window_title(title)
            if ws:
                return ws

    return None


ws = _resolve_workspace() or subprocess.run(
    [AEROSPACE, 'list-workspaces', '--focused'],
    capture_output=True, text=True,
).stdout.strip()

notify_dir = os.path.expanduser('~/.hammerspoon/notifications')
os.makedirs(notify_dir, exist_ok=True)

with open(f'{notify_dir}/{session_id[:8]}.json', 'w') as f:
    json.dump({
        'session_id': session_id,
        'label':      label,
        'workspace':  ws,
        'tmux_pane':  tmux_pane,
    }, f)
