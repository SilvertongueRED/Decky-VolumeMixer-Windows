# Decky Volume Mixer (Windows)

A per-app volume mixer for Decky Loader for Windows — control the volume of each running application from the Steam Big Picture / Game Mode quick-access menu, without leaving your game.

This is a Windows port of [allmazz/decky-volume-mixer](https://github.com/allmazz/decky-volume-mixer) (PipeWire/SteamOS). On Windows it talks to the **Windows Core Audio** API directly (pure Python `ctypes`/COM — no extra dependencies, no external tools). The original PipeWire backend is still in `main.py` and is used automatically on SteamOS.

## Features

- **Per-app volume control** — one slider per app that is currently playing audio
- **Real app names** — games are listed by their actual title, not an internal exe codename (e.g. `Discovery.exe` shows as **THE FINALS**); the underlying exe name is shown as a subtitle when it differs
- **Hide apps** — a controller-friendly "Hide apps" button toggles individual apps out of (or back into) the mixer, no regex needed
- **Reset** — set every app back to 100%
- **Filters & settings** — regex filters and a boost limit via the settings panel
- **Works with anti-cheat games** — apps are found through a process snapshot, so protected processes still appear

## How app names are resolved

For each audio session the plugin picks the first useful name from:

1. **Steam** — if the exe lives in a Steam library (`steamapps/common/<game>`), the game's name from its `appmanifest` is used. If an anti-cheat hides the process path, the plugin finds which installed Steam game ships that exe instead.
2. **Exe version info** — the file's *ProductName* / *FileDescription* (generic ones like "Unreal Engine" are ignored).
3. **Fallback** — the exe name, then the Windows session label.

`steamwebhelper` is shown as **Steam** (Steam UI, and music from Audio Loader). Apps you hid under an older exe-based name stay hidden.

## Install

1. Download `decky-volume-mixer-v0.2.0.zip` from the [Releases](../../releases) page.
2. Extract it so you end up with `...\homebrew\plugins\decky-volume-mixer\` containing `main.py`, `plugin.json`, `package.json` and `dist\`.
3. Restart Decky Loader (or reload plugins). **Volume Mixer** appears in the quick-access menu.

## Requirements

- Windows 10/11 with Decky Loader for Windows
- Python (provided by Decky) — no extra packages needed

## Build from source

The repository ships the compiled frontend in `dist/`, so no build step is needed to use it. The TypeScript source lives in the upstream project: [allmazz/decky-volume-mixer](https://github.com/allmazz/decky-volume-mixer).

## Credits

- Original plugin: [Kirill Nikiforov (allmazz)](https://github.com/allmazz/decky-volume-mixer)
- Windows port and app-name detection: [SilvertongueRED](https://github.com/SilvertongueRED)

Licensed under GPL-3.0-or-later (see `LICENSE`).
