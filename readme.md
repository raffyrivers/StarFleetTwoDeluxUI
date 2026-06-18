# Star Fleet II Delux UI Showcase

Pygame cockpit UI demo for a Star Fleet II style command screen.

## Requirements

- Python 3.12+
- FFmpeg with `ffprobe` on PATH
- Python packages from `requirements.txt`

## Setup

```powershell
python -m pip install -r requirements.txt
winget install --id Gyan.FFmpeg -e
```

Verify FFmpeg:

```powershell
ffmpeg -version
ffprobe -version
```

## Run

```powershell
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| `Esc` | Quit |
| `F11` | Toggle fullscreen |
| `1`-`8` | Toggle top alert indicators |
| `n` | Cycle primary display video |
| `i`, `o`, `p` | Navigation console views |
| `l`, `;`, `'` | Star map views |
| `q`, `w` | Engineering probe views |
| `z`, `x` | Hyperspace speed up/down |
| `c`, `v` | Space speed up/down |
| `F1`-`F4` | Ship damage display states |
| `d`, `f`, `g`, `h`, `j` | Combat display overlays |
| `m`, `,`, `.`, `/` | Shield modes |
| `Right Shift` | Target board |
| `9`, `0`, `-` | Communication display modes |

## Status Colors

| Color | Meaning |
| --- | --- |
| Green | Normal, ready, active |
| Yellow | Warning, low, caution |
| Red | Alert or selected combat state |
| Cyan | Labels and headings |
| Grey | Inactive controls |

## TODO

- [ ] Add mouse support for panel buttons.
- [ ] Replace remaining hardcoded placeholder data with a shared state model.
- [ ] Split large `Panel.py` drawing sections into smaller console modules.
- [ ] Add bounds checks for text-heavy panels at smaller window sizes.
- [ ] Add a simple startup check for missing FFmpeg/FFprobe.
