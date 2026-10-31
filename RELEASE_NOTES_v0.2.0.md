## Decky Volume Mixer (Windows) v0.2.0

### New
- **Real app names.** Games are now listed by their actual title. Steam games resolve via their appmanifest (e.g. `Discovery.exe` → **THE FINALS**), including games whose anti-cheat hides the process path.
- Falls back to the exe's ProductName/FileDescription, then the exe/session name.
- The underlying exe name is shown as a subtitle when it differs from the friendly name.
- `steamwebhelper` is labelled **Steam**.

### Notes
- Apps hidden under an old exe-based name stay hidden.

### Install
Download `decky-volume-mixer-v0.2.0.zip`, extract into `homebrew\plugins\`, restart Decky Loader.
