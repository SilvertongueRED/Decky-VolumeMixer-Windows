## decky-volume-mixer

Control the volume of individual applications directly from game mode using Pipewire.

### Features

- **Per-app volume control** — adjust the volume of each running application independently
- **Hide apps** — a controller-friendly "Hide apps" button lets you toggle individual apps out of (or back into) the mixer without typing regexes
- **Pipewire integration** — works natively with Pipewire via `pw-dump` and `wpctl`
- **Configurable** — tweak plugin behavior through the settings panel

### Build

```sh
make       # install deps, build, and package into build/decky-volume-mixer.zip
make build # install deps and build without packaging
make clean # remove dist and build directories
```

### Screenshots

| Main View | Settings |
|:---------:|:--------:|
| ![Main View](./assets/thumbnail.jpg) | ![Settings](./assets/thumbnail-settings.jpg) |
