#!/usr/bin/env python3
"""Install Hammerspoon modules onto the current device."""
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
HS_DIR = Path.home() / ".hammerspoon"

INIT_SNIPPET = """\
package.path = package.path .. ';' .. os.getenv('HOME') .. '/.hammerspoon/_mine/?.lua'
MonitorSwitch      = require('monitor_switch')
WorkspaceIndicator = require('workspace_indicator')
WindowFlash        = require('window_flash')
ClaudeNotifications = require('claude_notifications')"""


def check_prerequisites():
    app = Path("/Applications/Hammerspoon.app")
    cli = subprocess.run(["which", "hs"], capture_output=True).returncode == 0
    if not app.exists() and not cli:
        print("ERROR: Hammerspoon is not installed.")
        print("  Install: brew install --cask hammerspoon")
        print("  Then enable CLI access: Hammerspoon menu → Install CLI Tools")
        sys.exit(1)


check_prerequisites()

HS_DIR.mkdir(parents=True, exist_ok=True)

_mine_dst = HS_DIR / "_mine"
if _mine_dst.exists():
    shutil.rmtree(_mine_dst)
shutil.copytree(TOOL / "_mine" / "scripts", _mine_dst)
print(f"replaced {_mine_dst}/")

print()
print("One-time init.lua setup — ensure ~/.hammerspoon/init.lua contains:")
print()
for line in INIT_SNIPPET.splitlines():
    print(f"  {line}")
