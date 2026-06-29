# aerospace

## Installation

```sh
python3 aerospace/install.py
aerospace reload-config
```

## Required macOS settings

These must be configured manually before AeroSpace works correctly. Most are in **System Settings → Desktop & Dock → Mission Control**.

### Desktop & Dock

| Setting | Value | Notes |
|---------|-------|-------|
| Displays have separate Spaces | **OFF** | Required for AeroSpace to manage windows across monitors. Anchors the Dock to one display as a side effect. |
| Automatically rearrange Spaces based on most recent use | **OFF** | Keeps Space order stable. |
| When switching to an application, switch to a Space with open windows | **OFF** | Prevents macOS from hijacking workspace jumps. |
| Group windows by application | **ON** | AeroSpace recommendation — prevents parked windows from rendering tiny in Mission Control. |
| Automatically hide and show the Dock | **OFF** | |

### Mission Control

Remove all extra native Spaces — AeroSpace replaces them. Leave just one.

### Displays

- **Arrange**: Ensure each monitor has a free corner at the bottom so AeroSpace has somewhere to park hidden windows.
- **Main display**: Set your preferred monitor as Main so the Dock and menu bar live where you want them.

### Privacy & Security → Accessibility

Grant AeroSpace Accessibility permission, then **relaunch the app** — the permission only takes effect after a restart.
