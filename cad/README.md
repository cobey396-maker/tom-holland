# CAD: web shooter v0 (concept)

The 3D model is **code**: [`webshooter_cad.py`](webshooter_cad.py) uses [CadQuery](https://cadquery.readthedocs.io/). Every dimension is a named parameter at the top of the file, so you can change your wrist size, capsule size and so on, then regenerate all the parts.

![assembly](preview/assembly.png)

## Parts
| File | What | Printed? |
|---|---|---|
| `stl/bracer.stl` | Forearm shell + capsule clips + electronics tray + nozzle block | yes |
| `stl/tray_lid.stl` | Electronics cover with holes for the arm/safe switch and status LED | yes |
| `stl/palm_pad.stl` | Palm trigger pad (12 mm button) + thumb-side tether button (6 mm), strap slots | yes |
| capsules (blue) | Pressure-rated tubes, bought off the shelf | **NO: never print a pressure vessel** |

`webshooter_v0.step` is the full assembly.

## Viewing / editing without installing anything
- **GitHub:** click any `.stl` file in this folder; GitHub shows an interactive 3D viewer.
- **Tinkercad:** Create new design → Import → pick an `.stl`.
- **Onshape (free):** Import `webshooter_v0.step`.

## Regenerating
```bash
pip install cadquery matplotlib
python webshooter_cad.py      # writes stl/ and webshooter_v0.step
python render_preview.py      # writes preview/*.png
```

## Before printing at the makerspace
1. **Measure your wrist** over whatever sleeve you'll wear (width side-to-side and height top-to-bottom, ~5 cm back from the wrist bone) and update `WRIST_WIDTH` / `WRIST_HEIGHT`.
2. Update `CAPSULE_DIA` once the actual capsule tubes are chosen.
3. Print the bracer **standing on its back end** (the electronics-tray end): the shell and clips then need no supports.
4. Suggested: PETG or PLA, 20% infill, 3 walls. The v0 platform is chunky; trim it once the parts are real.
5. Cheap fit test first: set `BRACER_LENGTH = 30` and print a thin ring to check the wrist size before the full print.

## Known v0 limitations
- Capsule and electronics dimensions are placeholders until parts are picked.
- No routing channels for the tubing yet.
- No tether spool/hook at the nozzle yet (v1).
