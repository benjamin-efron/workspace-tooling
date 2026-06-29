#!/usr/bin/python3
"""Pass the newly focused monitor name to Hammerspoon for visual feedback."""
import subprocess

result = subprocess.run(
    ['/opt/homebrew/bin/aerospace', 'list-monitors', '--focused'],
    capture_output=True, text=True
)
# Output format: "1 | LG HDR WFHD (2)"
monitor = result.stdout.strip().split(' | ', 1)[-1]

subprocess.run(['/opt/homebrew/bin/hs', '-c', f"MonitorSwitch.onFocus('{monitor}')"])
