#!/usr/bin/env python3
"""Install Hammerspoon modules onto the current device."""
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
HS_DIR = Path.home() / ".hammerspoon"

INIT_SNIPPET = """\
package.path = package.path .. ';' .. os.getenv('HOME') .. '/.hammerspoon/internal/?.lua'
MonitorSwitch      = require('monitor_switch')
WorkspaceIndicator = require('workspace_indicator')
WindowFlash        = require('window_flash')"""


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

internal_dst = HS_DIR / "internal"
if internal_dst.exists():
    shutil.rmtree(internal_dst)
shutil.copytree(TOOL / "internal" / "scripts", internal_dst)
print(f"replaced {internal_dst}/")

print()
print("One-time init.lua setup — ensure ~/.hammerspoon/init.lua contains:")
print()
for line in INIT_SNIPPET.splitlines():
    print(f"  {line}")
