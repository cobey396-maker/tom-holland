# How it works

## The core trick: coaxial jetting

A **coaxial needle** is one needle inside another. Two fluids flow out at once:

```
        outer needle  ──►  sheath fluid  (triggers solidification)
        inner needle  ──►  core fluid    (becomes the fiber)
```

The sheath wraps the core stream so the reaction starts the instant the fluid leaves the tip — in the air, not in a bath. That's what turns "squirting liquid" into "shooting a web."

## Reference system (Tufts Silklab)

- **Core:** silk fibroin solution + dopamine
- **Sheath:** acetone
- Acetone makes silk proteins lock together (solidify). Dopamine makes it happen almost instantly and makes the fiber sticky (same chemistry barnacles use to glue to rocks).
- Acetone evaporates in flight → a dry-ish, adhesive fiber.
- Additives: **chitosan** (much stronger fibers), **borate buffer** (much stickier).
- Fiber thickness is set by the needle bore.

Sources: [Newswise](https://www.newswise.com/articles/inspired-by-spider-man-a-lab-recreates-web-slinging-technology), [The Engineer](https://theengineer.co.uk/content/news/web-slinging-device-shoots-fibres-that-can-pick-up-objects)

## Our budget system (Phases 1–3)

- **Core:** sodium alginate in water (1–3%)
- **Sheath:** calcium chloride in water (1–5%)
- Calcium ions cross-link alginate chains instantly → a gel strand. Same chemistry as "spherification" in cooking.
- Non-toxic, non-flammable, cheap. Gel fibers are weaker and wetter than silk — a stepping stone, not the final web.

## The device (target architecture)

```
 [palm trigger] ─► [ESP32] ─► [stepper driver] ─► [syringe pump: core]
                     │                         └► [syringe pump: sheath]
                     ├─► arm/safe switch, status LED
                     └─► Bluetooth telemetry ─► laptop/phone logger
```

## What we measure

- Jet speed and range
- Fiber length before break-up
- Success rate (did a continuous fiber form and stick?)
- Adhesion / tensile strength (hang weights until it fails)
- How these change with concentration, flow rate, and needle size
