# workspace-tooling

Portable workspace configuration for macOS. This repo is the source of truth — `scripts/install.sh` symlinks each tool's config from its standard OS location into this repo.

## What's here

| Tool | Config path | Notes |
|------|-------------|-------|
| [AeroSpace](https://github.com/nikitabobko/AeroSpace) | `~/.config/aerospace/aerospace.toml` | Tiling WM; scripts at `~/hq/aerospace/` |

## Setup on a new machine

```sh
git clone <repo-url> ~/Documents/Code/workspace-tooling
cd ~/Documents/Code/workspace-tooling
chmod +x scripts/install.sh
./scripts/install.sh
```

The script is idempotent — safe to re-run. Existing files are backed up with a `.bak` suffix before being replaced.

## Adding a new tool

1. Create a subdirectory: `mkdir <toolname>`
2. Move configs in: `mv ~/.config/<toolname> ./<toolname>/`
3. Add a `symlink` line to `scripts/install.sh`
4. Add a row to the table above
