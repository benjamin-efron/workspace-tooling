#!/usr/bin/env python3
"""Install aerospace config and scripts onto the current device."""
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "aerospace"


def check_prerequisites():
    if subprocess.run(["which", "aerospace"], capture_output=True).returncode != 0:
        print("ERROR: AeroSpace is not installed.")
        print("  Install: brew install --cask nikitabobko/tap/aerospace")
        sys.exit(1)


check_prerequisites()

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

toml = (TOOL / "_mine" / "config" / "aerospace.toml").read_text().replace("$HOME", str(Path.home()))
(CONFIG_DIR / "aerospace.toml").write_text(toml)
print(f"wrote    {CONFIG_DIR / 'aerospace.toml'}")

_mine_dst = CONFIG_DIR / "_mine"
if _mine_dst.exists():
    shutil.rmtree(_mine_dst)
shutil.copytree(TOOL / "_mine" / "scripts", _mine_dst)
print(f"replaced {_mine_dst}/")

old_internal = CONFIG_DIR / "internal"
if old_internal.exists():
    shutil.rmtree(old_internal)
    print(f"removed  {old_internal}/ (stale)")
