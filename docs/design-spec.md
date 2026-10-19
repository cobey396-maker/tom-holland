# Design spec (v0 — dream design)

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

## Proposed architecture
- Two small capsules (core fluid + sheath fluid), pressurized with air to ≤ 30–40 psi, with a pressure-relief valve
- **Pinch valves** on silicone tubing (fluid never touches the valve → fewer clogs), driven by the ESP32
- Palm switch → ESP32 → opens valves while held; on release closes valves, optional suck-back to clear the tip
- Arm/safe switch must be on before anything fires

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
