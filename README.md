# Tom Holland — Fluid-to-Fiber Web Shooter

A wrist-mounted device that shoots a liquid which solidifies into a sticky fiber mid-air — a real, working take on Spider-Man's web shooters.

> **Status:** Planning & design (Phase 0). No hardware purchased yet.

## The idea

Inspired by [Tufts Silklab's research](https://www.newswise.com/articles/inspired-by-spider-man-a-lab-recreates-web-slinging-technology) (Lo Presti & Omenetto, *Advanced Functional Materials*), where a silk-fibroin + dopamine solution is fired through a **coaxial needle** sheathed in acetone. The solvent triggers near-instant solidification and evaporates mid-flight, leaving an adhesive fiber that sticks to what it hits and can lift 80× its own weight.

This project builds toward that in phases:

| Phase | What | Chemistry | Cost |
|---|---|---|---|
| 0 | Design, simulation, firmware in a simulator | none | **$0** |
| 1 | Bench-top fluid-to-fiber rig | Sodium alginate + calcium chloride (food-safe, gels on contact) | ~$35 |
| 2 | Motorized pump + computer-vision analysis | same | ~$35 more |
| 3 | Wrist prototype (3D printed at NCAT makerspace) | same | filament |
| 4 | Real silk/dopamine fibers, in a university lab with faculty mentorship | Silk fibroin + dopamine + acetone | lab-supplied |

## Repo layout

```
docs/        how it works, roadmap, safety, parts list, brainstorm
firmware/    ESP32 code for the pump, trigger and safety interlocks
analysis/    Python: simulations, slow-mo video analysis, experiment data
cad/         housing and nozzle designs (Tinkercad / Onshape exports)
build-log/   dated entries: what was tried, what happened, photos/videos
```

## Start here

- [How it works](docs/how-it-works.md)
- [Roadmap](docs/roadmap.md)
- [Brainstorm & open questions](docs/brainstorm.md)
- [Safety](docs/safety.md)
- [Parts list](docs/parts-list.md)
