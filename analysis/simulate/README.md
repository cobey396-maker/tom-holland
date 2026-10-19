# Physics simulator

A first-order model of the web shooter: pressure and nozzle size in → jet speed, force, range, string length and shots per refill out.

```bash
pip install -r requirements.txt
python run_sim.py          # prints a report, saves plots to output/
python -m pytest -q        # sanity tests
```

## What it models
- **Jet speed:** Bernoulli (accelerating the fluid) + Hagen–Poiseuille (friction in the needle and tubing)
- **Jet force:** momentum flux, ρ·A·v²
- **Capsule:** air headspace expands as fluid leaves (Boyle's law), so pressure and jet speed fall during a shot
- **Soda can:** rigid-body sim; the can either tips about its bottom edge or slides on the table
- **Range:** ballistic from wrist height, no air drag

## Findings (v0, 2026-10-19)
See [`output/report.txt`](output/report.txt) and the plots in `output/`.

1. **Viscosity is the #1 unknown.** At 30 psi, 1% alginate makes a fine string jet (~6 m/s, ~3 m range); 2% alginate barely dribbles out of an 18G needle. Measuring the real viscosity is the first Phase 1 test.
2. **Impact mode needs its own short, wide path.** A long thin tube eats most of the pressure before the fluid reaches the nozzle. Plan: 3 mm nozzle fed by a short 5 mm tube.
3. **A full soda can is near the limit.** It takes ~1.25 N to tip one. That needs ~40 psi plus an extra air chamber, and one shot uses the whole capsule. **An empty can tips with a 10 ms tap, 8 shots per fill.** Demo target: empty or nearly empty can.
4. **The capsule's air headspace matters a lot.** With only 7.5 mL of air, the jet loses most of its speed within ~3 s of holding the trigger (~12 m of string). Adding a 60 mL air chamber doubles hold time and gives ~30 m of string. Alternative: a spring-loaded piston for constant pressure.

## Assumptions to replace with measurements
| Value | Guess | How to measure (Phase 1) |
|---|---|---|
| Alginate effective viscosity | 1%: 0.05 Pa·s, 2%: 0.3 Pa·s | time how long a syringe takes to empty through a needle |
| Nozzle discharge coefficient | 0.8 | measure flow rate (mL/s) at known pressure |
| Can friction | 0.4 | tilt the table until the can slides |
