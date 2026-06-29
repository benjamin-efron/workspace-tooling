# workspace-tooling

Portable macOS workspace configuration. Each top-level directory is a tool with an idempotent `install.py` that copies config and scripts to their expected OS locations.

## Tools

| Tool | What it does |
|------|-------------|
| [AeroSpace](https://github.com/nikitabobko/AeroSpace) | Tiling WM — keybindings, workspace layout, window rules |
| [Hammerspoon](https://www.hammerspoon.org) | Automation — window flash, workspace badge, monitor switch feedback |

## Setup on a new machine

```sh
git clone https://github.com/benjamin-efron/workspace-tooling
cd workspace-tooling

python3 aerospace/install.py
aerospace reload-config

python3 hammerspoon/install.py
# Follow the printed instructions to update ~/.hammerspoon/init.lua, then reload Hammerspoon
```

## Adding a new tool

1. Create a directory named after the tool.
2. Add `install.py` — copies `internal/` contents to their expected OS locations.
3. Add `internal/` with whatever structure the tool needs.
