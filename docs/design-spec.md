# Design spec (v0 — dream design)

## Decisions (2026-10-19)
- **Two modes:** tap = impact shot, hold = string. ✅
- **Refill port**, not swappable capsules. ✅
- **Web lifetime: 3–5 minutes**, then it dissolves. Tether pull window ≈ first 1–2 min. ✅

## Requirements
| # | Requirement | Status |
|---|---|---|
| R1 | Wristband form factor | design |
| R2 | Pressurized capsule holds the fluid | design |
| R3 | Palm switch (center of palm) fires | design |
| R4 | **Impact:** enough force to knock over / push a full soda can | needs testing |
| R5 | **Adhesion:** stick a sheet of paper to a wall | needs testing |
| R6 | **String mode:** hold = continuous strand, release = strand ends | design |
| R7 | Fluid → hardened, silky fiber in mid-air | Phase 1 (alginate), Phase 4 (silk) |
| R8 | **Dissolves over time** after being shot | research |
| R9 | **Tether mode:** second button keeps the string attached to the wrist so you can pull things before it dissolves | design |
| — | ~~Push someone's hand back~~ | **Dropped:** see Safety. Never aimed at people. |

## Rough physics (to be refined by `analysis/simulate`)
Jet force ≈ ρ · A · v²  (fluid density × nozzle area × speed²)

To get ~1 N (roughly what tips a full soda can) with a water-like fluid:
- v ≈ 20 m/s, nozzle ≈ 1.8 mm → pressure ≈ 30 psi, flow ≈ 50 mL/s
- A 0.2 s burst uses ~10 mL.

**Key conflict:** impact wants a *thick, fast* jet; fiber formation wants a *thin* coaxial jet.
→ Proposed solution: **two modes**
- **Tap = impact shot:** short, wide burst
- **Hold = string mode:** thin coaxial strand, valve closes on release

## Wearing it
Shooter on the **inner wrist** (palm side), same side as the palm trigger. Fire with the hand bent back (thwip pose): with the wrist straight, your own palm and the trigger pad are in the jet's path.
- **Planned safety interlock:** a tiny motion sensor in the palm pad plus one in the pod lets the firmware measure the wrist angle and only fire when the hand is bent back.

## Proposed architecture
- Two small capsules (core fluid + sheath fluid), pressurized with air to ≤ 30–40 psi, with a pressure-relief valve
- **Pinch valves** on silicone tubing (fluid never touches the valve → fewer clogs), driven by the ESP32
- Palm switch → ESP32 → opens valves while held; on release closes valves, optional suck-back to clear the tip
- Arm/safe switch must be on before anything fires

## Tether mode (R9)
**Controls:** a two-button palm pad built into the band on a flexible tongue (see `cad/README.md`): **FIRE** under the middle/ring fingers, **TETHER** next to it, recessed. Holding TETHER picks what happens on release:
- Release palm only → valves close, string breaks off (normal)
- Hold tether button while releasing → a small motorized hook/spool at the nozzle catches and winds the string end, anchoring it to the wrist

**Pulling:** pull with your arm, or let the spool reel it in (reel speed + motor current gives a rough pull-force reading).

**Strength reality check (estimates, to be measured):**
| Fiber | Rough pull capacity (1 mm strand) |
|---|---|
| Wet alginate gel | tens of grams: paper, a pen, a phone charger |
| Alginate + chitosan / multiple strands | more; to be tested |
| Silk + dopamine + chitosan (Phase 4) | much stronger per weight |
| Hybrid: gel coated on a water-soluble (PVA) thread | strongest, and the thread dissolves in water too. Stretch goal |

**Dissolve vs. pull:** strength drops as the fiber breaks down, so the dissolve timer must leave a usable window (e.g. strong for the first few minutes). Measuring strength over time is a key experiment.

## Refill port
- Each capsule: **luer-lock fill port with a one-way check valve** (refill with a plain syringe) + a **Schrader valve** (the bike-tire valve) to pressurize with any bike pump.
- **Bleed valve** to vent pressure before refilling; firmware/LED should warn if pressurized.
- **Pressure-relief valve** set ~40 psi so a bike pump can't over-pressurize it.

## Dissolving in 3–5 minutes
Enzymes (option C below) are probably too slow for minutes. Faster candidate:
- **Built-in citrate timer:** add a small, tuned amount of **sodium citrate** to the core fluid. The calcium-rich sheath gels the outside instantly; then the citrate slowly pulls calcium back out of the gel and it softens and falls apart. More citrate means faster dissolving, and too much means it never forms. Finding the sweet spot is the experiment.
- Fallback: weakly cross-linked gel (less calcium) that slumps and breaks within minutes.

**Test plan:** sweep citrate amount → measure (a) does a fiber form, (b) pull strength at 0/1/2 min, (c) time until it breaks or dissolves. Automate (c) with a phone timelapse + OpenCV detecting when the strand breaks.

## Dissolving (R8): options
| Option | How | Difficulty |
|---|---|---|
| A. Dissolver spray | Alginate-calcium gel dissolves when calcium is pulled out: spray with sodium citrate solution (cheap, food-safe) | easy |
| B. Dry & flake | Gel dries out, turns brittle, and falls off | free, but not really "dissolving" |
| C. Built-in timer | Put a small amount of an alginate-digesting enzyme (alginate lyase) in the sheath; the fiber breaks itself down over hours. Concentration tunes the timer | research-grade, novel |
| D. Silk version | Less solvent treatment = more water-soluble silk; tune how long it lasts | Phase 4, lab |

Plan: A as the baseline, C as the headline experiment ("programmable-lifetime fiber").

## Safety constraints from this spec
- High pressure through a fine nozzle can inject fluid through skin (a serious medical emergency). Cap pressure, never aim at skin.
- Impact testing only against objects (cans, targets), with eye protection.
