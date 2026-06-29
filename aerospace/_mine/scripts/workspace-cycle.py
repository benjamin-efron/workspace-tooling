#!/usr/bin/python3
"""Cycle to the next or previous workspace on the focused monitor."""
import subprocess
import sys

direction = sys.argv[1]   # 'next' or 'prev'
ordered   = sys.argv[2:]  # desired workspace order, passed from aerospace.toml

current = subprocess.run(
    ['/opt/homebrew/bin/aerospace', 'list-workspaces', '--focused'],
    capture_output=True, text=True
).stdout.strip()

on_monitor = set(subprocess.run(
    ['/opt/homebrew/bin/aerospace', 'list-workspaces', '--monitor', 'focused'],
    capture_output=True, text=True
).stdout.strip().splitlines())

# Filter to workspaces on the focused monitor, preserving the requested order.
workspaces = [w for w in ordered if w in on_monitor]

if not workspaces:
    sys.exit(0)

try:
    idx = workspaces.index(current)
except ValueError:
    idx = 0

if direction == 'next':
    target = workspaces[(idx + 1) % len(workspaces)]
else:
    target = workspaces[(idx - 1) % len(workspaces)]

subprocess.run(['/opt/homebrew/bin/aerospace', 'workspace', target])
