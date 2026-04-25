
# RandChords

A terminal-based random chord progression generator with playback.

## Installation

```bash
pip install randchord
```

## Usage

```bash
randchord               # start fresh
randchord file.crdprog  # open a saved progression list
```

## Controls

| Key | Action |
|-----|--------|
| Ctrl+N | Generate new random progression |
| Ctrl+R | Replay current progression |
| Ctrl+A | Add current progression to table |
| Ctrl+P | Play selected progression |
| Ctrl+W | Save table to file |
| Ctrl+C | Quit |

## File Format

RandChords saves progressions as `.crdprog` files — plain text, one progression per line:

```
Am | F | C | G
Dm | Bb | F | C
```

Any text format works too, just name your file with the extension you want.

## License

MIT
