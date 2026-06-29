#!/usr/bin/env python3
"""Install tmux config onto the current device."""
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent


def check_prerequisites():
    if subprocess.run(["which", "tmux"], capture_output=True).returncode != 0:
        print("ERROR: tmux is not installed.")
        print("  Install: brew install tmux")
        sys.exit(1)


check_prerequisites()

dst = Path.home() / ".tmux.conf"
shutil.copy(TOOL / "internal" / "tmux.conf", dst)
print(f"wrote    {dst}")
print()
print("If TPM is not installed, bootstrap it:")
print("  git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm")
print("  tmux source ~/.tmux.conf")
print("  Then press prefix + I inside tmux to install plugins.")
