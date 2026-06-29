#!/usr/bin/python3
"""Triggered by AeroSpace on-focused-workspace-changed."""
import os
import subprocess

workspace = os.environ.get('AEROSPACE_FOCUSED_WORKSPACE', '')
if workspace:
    subprocess.run(['/opt/homebrew/bin/hs', '-c', f"WorkspaceIndicator.show('{workspace}')"])

result = subprocess.run(
    ['/opt/homebrew/bin/aerospace', 'list-monitors', '--focused'],
    capture_output=True, text=True
)
monitor = result.stdout.strip().split(' | ', 1)[-1]
if monitor:
    subprocess.run(['/opt/homebrew/bin/hs', '-c', f"MonitorSwitch.onFocus('{monitor}')"])
