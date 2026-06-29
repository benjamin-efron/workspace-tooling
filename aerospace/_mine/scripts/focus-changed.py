#!/usr/bin/python3
"""Triggered by AeroSpace on-focus-changed. Flashes a border around the focused window."""
import subprocess

subprocess.run(['/opt/homebrew/bin/hs', '-c', 'WindowFlash.show()'])
