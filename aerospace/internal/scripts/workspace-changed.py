#!/usr/bin/python3
"""Triggered by AeroSpace on-focused-workspace-changed. Shows workspace indicator."""
import os
import subprocess

workspace = os.environ.get('AEROSPACE_FOCUSED_WORKSPACE', '')
if workspace:
    subprocess.run(['/opt/homebrew/bin/hs', '-c', f"WorkspaceIndicator.show('{workspace}')"])
