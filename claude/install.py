#!/usr/bin/env python3
"""Install Claude Code hooks onto the current device."""
import shutil
from pathlib import Path

TOOL = Path(__file__).resolve().parent
CLAUDE_DIR = Path.home() / '.claude'

_CMD = 'python3 ~/.claude/_mine/hooks/notify.py'
_ENTRY = f'[{{"matcher": "", "hooks": [{{"type": "command", "command": "{_CMD}"}}]}}]'
HOOK_LINES = [
    f'"Notification": {_ENTRY}',
    f'"Stop": {_ENTRY}',
]

CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

_mine_dst = CLAUDE_DIR / '_mine'
if _mine_dst.exists():
    shutil.rmtree(_mine_dst)
shutil.copytree(TOOL / '_mine', _mine_dst)
print(f'replaced {_mine_dst}/')

# Clean up old install location if present
old_hook = CLAUDE_DIR / 'hooks' / 'notify.py'
if old_hook.exists():
    old_hook.unlink()
    print(f'removed  {old_hook} (stale)')

settings = CLAUDE_DIR / 'settings.json'
print()
if not settings.exists():
    print('~/.claude/settings.json not found — create it with:')
    print()
    print('  {')
    print('    "hooks": {')
    for i, line in enumerate(HOOK_LINES):
        suffix = ',' if i < len(HOOK_LINES) - 1 else ''
        print(f'      {line}{suffix}')
    print('    }')
    print('  }')
else:
    print('Ensure ~/.claude/settings.json includes Notification and Stop hooks:')
    print()
    print('  "hooks": {')
    for i, line in enumerate(HOOK_LINES):
        suffix = ',' if i < len(HOOK_LINES) - 1 else ''
        print(f'    {line}{suffix}')
    print('  }')

print()
print("Also ensure ~/.hammerspoon/init.lua contains:")
print()
print("  ClaudeNotifications = require('claude_notifications')")
