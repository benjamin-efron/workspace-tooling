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


def _resolve_window():
    """Return (workspace, window-id) of the Ghostty window hosting this tmux session.

    tmux's set-titles-string ('#S', see tmux.conf) makes the Ghostty window title
    equal the tmux session name, so we can match it directly against AeroSpace's
    window list without needing per-terminal tty info (which Ghostty's AppleScript
    dictionary doesn't expose).
    """
    if not tmux_pane:
        return None, None

    session = subprocess.run(
        [TMUX, 'display-message', '-t', tmux_pane, '-p', '#{session_name}'],
        capture_output=True, text=True,
    ).stdout.strip()
    if not session:
        return None, None

    r = subprocess.run(
        [AEROSPACE, 'list-windows', '--all', '--json'],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None, None
    try:
        windows = json.loads(r.stdout)
    except Exception:
        return None, None
    for w in windows:
        if w.get('app-name') == 'Ghostty' and w.get('window-title', '') == session:
            return w.get('workspace'), w.get('window-id')
    return None, None


focused_ws = subprocess.run(
    [AEROSPACE, 'list-workspaces', '--focused'],
    capture_output=True, text=True,
).stdout.strip()

resolved_ws, window_id = _resolve_window()
ws = resolved_ws or focused_ws

pane_status = ''
suppressed = False
# Skip only if we positively resolved the session's real workspace and it
# matches current focus — a failed resolution must never be treated as a match.
if tmux_pane and resolved_ws and resolved_ws == focused_ws:
    pane_status = subprocess.run(
        [TMUX, 'display-message', '-t', tmux_pane, '-p', '#{window_active}#{pane_active}'],
        capture_output=True, text=True,
    ).stdout.strip()
    suppressed = pane_status == '11'

debug_log = os.path.expanduser('~/.claude/notify-debug.log')
with open(debug_log, 'a') as f:
    f.write(json.dumps({
        'session_id':  session_id[:8],
        'tmux_pane':   tmux_pane,
        'resolved_ws': resolved_ws,
        'window_id':   window_id,
        'focused_ws':  focused_ws,
        'ws':          ws,
        'pane_status': pane_status,
        'suppressed':  suppressed,
    }) + '\n')

if suppressed:
    sys.exit(0)

notify_dir = os.path.expanduser('~/.hammerspoon/notifications')
os.makedirs(notify_dir, exist_ok=True)

with open(f'{notify_dir}/{session_id[:8]}.json', 'w') as f:
    json.dump({
        'session_id': session_id,
        'label':      label,
        'workspace':  ws,
        'tmux_pane':  tmux_pane,
        'window_id':  window_id,
    }, f)
