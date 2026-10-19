"""Physics model for the web shooter.

Everything is SI units internally (Pa, m, s, kg). Helpers convert from psi / mm / mL.
The numbers are first-order estimates meant to guide design, not replace testing.
"""
from dataclasses import dataclass, replace
import math

G = 9.81                 # m/s^2
PSI = 6894.76            # Pa per psi
ATM = 101325.0           # Pa


# ---------------------------------------------------------------- inputs

@dataclass(frozen=True)
class Fluid:
    name: str
    density: float       # kg/m^3
    viscosity: float     # Pa*s (effective viscosity at nozzle shear rates)


# Alginate is shear-thinning, so the effective viscosity in a nozzle is lower than
# the "at rest" value. These are rough guesses -- measuring them is a Phase 1 task.
WATER = Fluid("water", 1000.0, 0.001)
ALGINATE_1PCT = Fluid("alginate 1%", 1005.0, 0.05)
ALGINATE_2PCT = Fluid("alginate 2%", 1010.0, 0.3)
FLUIDS = {f.name: f for f in (WATER, ALGINATE_1PCT, ALGINATE_2PCT)}


@dataclass(frozen=True)
class Nozzle:
    name: str
    diameter: float      # m, exit bore
    length: float        # m, length of the narrow bore
    cd: float = 0.8      # discharge coefficient (inertial losses at the exit)


# 18 gauge blunt needle: ID ~0.84 mm, 1/2" long
STRING_NOZZLE = Nozzle("string (18G needle)", 0.84e-3, 12.7e-3)
IMPACT_NOZZLE = Nozzle("impact (3 mm)", 3.0e-3, 5e-3)


@dataclass(frozen=True)
class Plumbing:
    tube_diameter: float = 3.0e-3   # m, silicone tube ID
    tube_length: float = 0.15       # m, capsule -> nozzle


# Impact mode needs its own short, wide path: thick fluid through a long thin tube
# loses most of its pressure to friction before it reaches the nozzle.
STRING_PLUMBING = Plumbing()
IMPACT_PLUMBING = Plumbing(tube_diameter=5.0e-3, tube_length=0.08)


@dataclass(frozen=True)
class Capsule:
    volume: float                   # m^3, total internal volume
    fluid_volume: float             # m^3, fluid loaded (rest is pressurized air)
    pressure_psi: float             # gauge pressure after pumping

    @property
    def gas_volume(self) -> float:
        return self.volume - self.fluid_volume


@dataclass(frozen=True)
class SodaCan:
    mass: float = 0.385             # kg, full 12 oz can
    radius: float = 0.033           # m
    height: float = 0.122           # m
    friction: float = 0.4           # can on a table
    hit_height: float = 0.10        # m, where the jet hits


def mm(x): return x * 1e-3
def ml(x): return x * 1e-6


# ---------------------------------------------------------------- jet

def exit_velocity(p_gauge: float, fluid: Fluid, nozzle: Nozzle,
                  plumbing: Plumbing = Plumbing()) -> float:
    """Jet speed (m/s) for a given driving pressure (Pa).

    Pressure is spent on two things:
      * accelerating the fluid:  rho v^2 / (2 Cd^2)            (Bernoulli)
      * viscous friction:        32 mu L v / d^2 per section    (Hagen-Poiseuille)
    Solve a v^2 + b v - P = 0 for v.
    """
    if p_gauge <= 0:
        return 0.0
    d, dt = nozzle.diameter, plumbing.tube_diameter
    a = fluid.density / (2 * nozzle.cd ** 2)
    b_nozzle = 32 * fluid.viscosity * nozzle.length / d ** 2
    # tube flow is slower by the area ratio; express its loss in terms of exit speed v
    b_tube = 32 * fluid.viscosity * plumbing.tube_length * (d / dt) ** 2 / dt ** 2
    b = b_nozzle + b_tube
    return (-b + math.sqrt(b * b + 4 * a * p_gauge)) / (2 * a)


def area(nozzle: Nozzle) -> float:
    return math.pi * nozzle.diameter ** 2 / 4


def flow_rate(v: float, nozzle: Nozzle) -> float:
    """Volumetric flow (m^3/s)."""
    return area(nozzle) * v


def jet_force(v: float, fluid: Fluid, nozzle: Nozzle) -> float:
    """Force (N) on a flat target the jet hits head-on and splashes off sideways."""
    return fluid.density * area(nozzle) * v ** 2


def reynolds(v: float, fluid: Fluid, nozzle: Nozzle) -> float:
    return fluid.density * v * nozzle.diameter / fluid.viscosity


def horizontal_range(v: float, launch_height: float = 1.2, angle_deg: float = 0.0) -> float:
    """How far the jet travels before hitting the floor (no air drag)."""
    th = math.radians(angle_deg)
    vx, vy = v * math.cos(th), v * math.sin(th)
    t = (vy + math.sqrt(vy * vy + 2 * G * launch_height)) / G
    return vx * t


# ---------------------------------------------------------------- capsule

def capsule_pressure(capsule: Capsule, fluid_used: float) -> float:
    """Gauge pressure (Pa) after `fluid_used` m^3 has left (isothermal air expansion)."""
    p0_abs = capsule.pressure_psi * PSI + ATM
    v_gas = capsule.gas_volume + fluid_used
    return p0_abs * capsule.gas_volume / v_gas - ATM


def fire(capsule: Capsule, fluid: Fluid, nozzle: Nozzle, duration: float,
         fluid_used: float = 0.0, plumbing: Plumbing = Plumbing(), dt: float = 1e-3):
    """Simulate one trigger press. Returns (fluid_used_after, list of (t, v, force)).

    Pressure falls as the capsule empties, so the jet weakens during the shot.
    """
    trace = []
    t = 0.0
    while t < duration and fluid_used < capsule.fluid_volume:
        p = capsule_pressure(capsule, fluid_used)
        v = exit_velocity(p, fluid, nozzle, plumbing)
        if v <= 0:
            break
        trace.append((t, v, jet_force(v, fluid, nozzle)))
        fluid_used = min(capsule.fluid_volume, fluid_used + flow_rate(v, nozzle) * dt)
        t += dt
    return fluid_used, trace


# ---------------------------------------------------------------- soda can

def can_static_thresholds(can: SodaCan = SodaCan()):
    """(force to start tipping, force to start sliding) in N."""
    tip = can.mass * G * can.radius / can.hit_height
    slide = can.friction * can.mass * G
    return tip, slide


def can_response(force_trace, dt: float = 1e-3, can: SodaCan = SodaCan(),
                 min_slide: float = 0.01) -> str:
    """Rigid-body sim of a soda can hit by the jet.

    The can either rocks about its far bottom edge or slides on the table, whichever
    the force overcomes first. force_trace: list of (t, v, force) from `fire`.
    Returns "tips", "slides" (moved more than `min_slide` m), or "stays".
    """
    tip_f, slide_f = can_static_thresholds(can)
    r, h, m = can.radius, can.height, can.mass
    inertia = m * (3 * r * r + h * h) / 12 + m * (r * r + (h / 2) ** 2)
    critical = math.atan2(2 * r, h)          # tilt where the center of mass passes the pivot
    friction = can.friction * m * G

    theta = omega = x = vx = 0.0
    forces = [f for _, _, f in force_trace]
    # keep running after the burst so the can can finish falling, rocking or sliding
    for i in range(len(forces) + 2000):
        f = forces[i] if i < len(forces) else 0.0
        arm = 2 * r * math.sin(theta) + can.hit_height * math.cos(theta)
        restoring = m * G * (r * math.cos(theta) - (h / 2) * math.sin(theta))
        if theta > 0 or f * arm > restoring:
            omega += (f * arm - restoring) / inertia * dt
            theta += omega * dt
            if theta <= 0:
                theta, omega = 0.0, 0.0
            if theta >= critical:
                return "tips"
        if vx > 0 or f > friction:
            vx = max(0.0, vx + (f - friction) / m * dt)
            x += vx * dt
    return "slides" if x > min_slide else "stays"


def min_burst_to_move(capsule, fluid, nozzle, plumbing=Plumbing(), can=SodaCan(),
                      max_duration=1.0, step=0.01):
    """Shortest tap (s) from a full capsule that tips or pushes the can.

    Returns (seconds, "tips" | "slides"), or (None, "stays").
    """
    d = step
    while d <= max_duration + 1e-9:
        _, trace = fire(capsule, fluid, nozzle, d, plumbing=plumbing)
        outcome = can_response(trace, can=can) if trace else "stays"
        if outcome != "stays":
            return d, outcome
        d += step
    return None, "stays"


def shots_per_fill(capsule, fluid, nozzle, burst, plumbing=Plumbing(), can=SodaCan()):
    """How many taps of length `burst` still tip or push the can, starting full."""
    used, shots = 0.0, 0
    while used < capsule.fluid_volume:
        used, trace = fire(capsule, fluid, nozzle, burst, used, plumbing)
        if not trace or can_response(trace, can=can) == "stays":
            break
        shots += 1
    return shots


def string_hold_time(capsule, fluid, nozzle, min_speed=2.0, plumbing=Plumbing()):
    """Seconds of continuous string before the jet drops below `min_speed` (m/s).

    Returns (seconds, total string length in m).
    """
    used, _ = 0.0, None
    used, trace = fire(capsule, fluid, nozzle, 60.0, used, plumbing)
    t_ok, length = 0.0, 0.0
    for i, (t, v, _) in enumerate(trace):
        if v < min_speed:
            break
        t_next = trace[i + 1][0] if i + 1 < len(trace) else t + 1e-3
        length += v * (t_next - t)
        t_ok = t_next
    return t_ok, length


def with_pressure(capsule: Capsule, psi: float) -> Capsule:
    return replace(capsule, pressure_psi=psi)


def impulse_to_tip(can: SodaCan = SodaCan()) -> float:
    """Momentum (N*s) a very short hit must deliver to tip the can over.

    The hit spins the can about its far bottom edge; it falls if that spin carries
    the center of mass over the pivot: 1/2 I w^2 >= m g (rise of center of mass).
    """
    r, h, m = can.radius, can.height, can.mass
    inertia = m * (3 * r * r + h * h) / 12 + m * (r * r + (h / 2) ** 2)
    rise = math.hypot(r, h / 2) - h / 2
    omega = math.sqrt(2 * m * G * rise / inertia)
    return inertia * omega / can.hit_height
