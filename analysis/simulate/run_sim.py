"""Run the web shooter design study: prints a report and saves plots to ./output.

    python run_sim.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from webshooter_sim import (
    ALGINATE_1PCT, ALGINATE_2PCT, FLUIDS, IMPACT_NOZZLE, IMPACT_PLUMBING, STRING_NOZZLE, PSI,
    Capsule, Nozzle, Plumbing, SodaCan, can_static_thresholds, exit_velocity, flow_rate, horizontal_range,
    impulse_to_tip, jet_force, min_burst_to_move, ml, mm, reynolds, shots_per_fill, string_hold_time,
    with_pressure,
)

OUT = Path(__file__).parent / "output"

# A wrist-sized capsule: ~20 mm x 80 mm inside = ~25 mL, 70% fluid / 30% air
WRIST_CAPSULE = Capsule(volume=ml(25), fluid_volume=ml(17.5), pressure_psi=30)
# Same capsule but with a separate 60 mL air chamber feeding it
BIG_AIR_CAPSULE = Capsule(volume=ml(17.5 + 60), fluid_volume=ml(17.5), pressure_psi=30)


def report():
    tip_f, slide_f = can_static_thresholds()
    print(f"Soda can: needs ~{tip_f:.2f} N to start tipping, ~{slide_f:.2f} N to slide\n")

    print("Jet at 30 psi (full capsule)")
    print(f"{'fluid':<13}{'nozzle':<22}{'speed m/s':>10}{'force N':>9}"
          f"{'flow mL/s':>11}{'range m':>9}{'Re':>8}")
    for fluid in FLUIDS.values():
        for nz in (IMPACT_NOZZLE, STRING_NOZZLE):
            pl = IMPACT_PLUMBING if nz is IMPACT_NOZZLE else Plumbing()
            v = exit_velocity(30 * PSI, fluid, nz, pl)
            print(f"{fluid.name:<13}{nz.name:<22}{v:>10.1f}{jet_force(v, fluid, nz):>9.2f}"
                  f"{flow_rate(v, nz) * 1e6:>11.1f}{horizontal_range(v):>9.1f}"
                  f"{reynolds(v, fluid, nz):>8.0f}")

    print("\nImpact mode with 1% alginate (3 mm nozzle, short 5 mm tube)")
    for label, cap in (("wrist capsule, 30 psi, 7.5 mL air", WRIST_CAPSULE),
                       ("+ 60 mL air chamber, 30 psi", BIG_AIR_CAPSULE),
                       ("+ 60 mL air chamber, 40 psi", with_pressure(BIG_AIR_CAPSULE, 40))):
        burst, outcome = min_burst_to_move(cap, ALGINATE_1PCT, IMPACT_NOZZLE, IMPACT_PLUMBING)
        if burst is None:
            print(f"  {label}: can doesn't move")
            continue
        shots = shots_per_fill(cap, ALGINATE_1PCT, IMPACT_NOZZLE, burst, IMPACT_PLUMBING)
        print(f"  {label}: {burst * 1000:.0f} ms tap -> can {outcome}; "
              f"shots per fill = {shots}")

    print("\n  Other targets (wrist capsule, 30 psi, no extra air chamber):")
    for name, mass in (("empty can", 0.015), ("quarter-full can", 0.10), ("half-full can", 0.20)):
        can = SodaCan(mass=mass)
        burst, outcome = min_burst_to_move(WRIST_CAPSULE, ALGINATE_1PCT, IMPACT_NOZZLE,
                                           IMPACT_PLUMBING, can=can)
        if burst is None:
            print(f"    {name:<17} doesn't move")
        else:
            shots = shots_per_fill(WRIST_CAPSULE, ALGINATE_1PCT, IMPACT_NOZZLE, burst,
                                   IMPACT_PLUMBING, can=can)
            print(f"    {name:<17} {burst * 1000:.0f} ms tap -> {outcome}; shots per fill = {shots}")
    j = impulse_to_tip()
    print(f"  A quick 'slug' hit instead needs ~{j:.3f} N*s of momentum: e.g. "
          f"{j / 10 * 1000:.0f} g of fluid at 10 m/s")

    print("\nWhat it takes to tip the can with a steady jet (full capsule, short 5 mm tube)")
    for fluid in (FLUIDS["water"], ALGINATE_1PCT):
        for d in (2.0, 2.5, 3.0, 4.0):
            nz = Nozzle(f"{d} mm", mm(d), mm(5))
            for psi in (20, 30, 40, 50, 60):
                v = exit_velocity(psi * PSI, fluid, nz, IMPACT_PLUMBING)
                if jet_force(v, fluid, nz) > tip_f:
                    print(f"  {fluid.name:<12} {d} mm nozzle: >= {psi} psi "
                          f"(uses {flow_rate(v, nz) * 1e5:.0f} mL per 0.1 s)")
                    break
            else:
                print(f"  {fluid.name:<12} {d} mm nozzle: not even at 60 psi")

    print("\nString mode (18G needle), string usable while jet > 2 m/s")
    for label, cap in (("wrist capsule", WRIST_CAPSULE), ("+ 60 mL air chamber", BIG_AIR_CAPSULE)):
        for fluid in (ALGINATE_1PCT, ALGINATE_2PCT):
            secs, length = string_hold_time(cap, fluid, STRING_NOZZLE)
            print(f"  {label:<20} {fluid.name:<12} hold {secs:5.1f} s -> {length:5.1f} m of string")


def plots():
    OUT.mkdir(exist_ok=True)
    pressures = [p for p in range(5, 61)]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for fluid in FLUIDS.values():
        ax.plot(pressures, [jet_force(exit_velocity(p * PSI, fluid, IMPACT_NOZZLE, IMPACT_PLUMBING), fluid,
                                      IMPACT_NOZZLE) for p in pressures], label=fluid.name)
    tip_f, _ = can_static_thresholds()
    ax.axhline(tip_f, ls="--", c="gray")
    ax.text(6, tip_f * 1.04, "force to tip a soda can", color="gray")
    ax.set(xlabel="capsule pressure (psi)", ylabel="jet force (N)",
           title="Impact mode: jet force vs pressure (3 mm nozzle)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "impact_force_vs_pressure.png", dpi=120)

    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ds = np.linspace(1.0, 4.0, 61)
    ps = np.linspace(5, 60, 56)
    for fluid, color in ((FLUIDS["water"], "C0"), (ALGINATE_1PCT, "C1")):
        force = np.array([[jet_force(exit_velocity(p * PSI, fluid, Nozzle("", mm(d), mm(5)),
                                                   IMPACT_PLUMBING),
                                     fluid, Nozzle("", mm(d), mm(5))) for d in ds] for p in ps])
        cs = ax.contour(ds, ps, force, levels=[tip_f], colors=color)
        ax.clabel(cs, fmt={tip_f: fluid.name}, fontsize=9)
    ax.axhline(40, ls=":", c="red")
    ax.text(1.05, 41, "40 psi safety cap", color="red")
    ax.set(xlabel="impact nozzle diameter (mm)", ylabel="capsule pressure (psi)",
           title="Above each line, a steady jet tips a full soda can")
    fig.tight_layout()
    fig.savefig(OUT / "can_tipping_map.png", dpi=120)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    gauges = {"14G (1.6 mm)": 1.6, "18G (0.84 mm)": 0.84, "22G (0.41 mm)": 0.41}
    for label, d in gauges.items():
        nz = Nozzle(label, mm(d), mm(12.7))
        ax.plot(pressures, [exit_velocity(p * PSI, ALGINATE_1PCT, nz) for p in pressures],
                label=label)
    ax.set(xlabel="capsule pressure (psi)", ylabel="jet speed (m/s)",
           title="String mode: 1% alginate jet speed by needle size")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "string_speed_by_needle.png", dpi=120)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    from webshooter_sim import fire
    for label, cap in (("wrist capsule (7.5 mL air)", WRIST_CAPSULE),
                       ("+ 60 mL air chamber", BIG_AIR_CAPSULE)):
        _, trace = fire(cap, ALGINATE_1PCT, STRING_NOZZLE, 30.0)
        ax.plot([t for t, _, _ in trace], [v for _, v, _ in trace], label=label)
    ax.set(xlabel="seconds holding the trigger", ylabel="jet speed (m/s)",
           title="String mode: jet slows as the capsule empties")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "string_speed_over_time.png", dpi=120)
    print(f"\nPlots saved to {OUT}")


if __name__ == "__main__":
    report()
    plots()
