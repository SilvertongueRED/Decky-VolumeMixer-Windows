## Decky Volume Mixer v0.3.0 — one zip for Windows and Steam Deck

### New
- **Single package for both platforms.** The same zip installs on Decky Loader for Windows and on Steam Deck / SteamOS. The audio backend is picked automatically: Windows Core Audio on Windows, PipeWire (`pw-dump` + `wpctl`) on SteamOS.
- Rewrote the install instructions and README for both platforms.

### Notes
- No plugin code changes; the SteamOS path was checked against simulated PipeWire output (list, set volume, hide, settings, reset). Real-hardware reports from Steam Deck users are welcome.

### Install
Download `decky-volume-mixer-v0.3.0.zip`.
- **Steam Deck:** Decky Settings -> Developer -> Install Plugin from ZIP.
- **Windows:** extract into `homebrew\plugins\`, restart Decky Loader.
