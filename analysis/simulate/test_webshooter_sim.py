import math
import pytest
from webshooter_sim import (
    ALGINATE_1PCT, ALGINATE_2PCT, IMPACT_NOZZLE, PSI, WATER, Capsule, Nozzle, Plumbing,
    can_response, can_static_thresholds, capsule_pressure, exit_velocity, fire,
    impulse_to_tip, jet_force, ml, mm,
)


def test_water_jet_matches_bernoulli_when_viscosity_negligible():
    nz = Nozzle("big", mm(3), mm(1), cd=1.0)
    p = 30 * PSI
    assert exit_velocity(p, WATER, nz, Plumbing(tube_length=0)) == pytest.approx(math.sqrt(2 * p / 1000), rel=0.02)


def test_thicker_fluid_is_slower():
    p = 30 * PSI
    assert (exit_velocity(p, WATER, IMPACT_NOZZLE)
            > exit_velocity(p, ALGINATE_1PCT, IMPACT_NOZZLE)
            > exit_velocity(p, ALGINATE_2PCT, IMPACT_NOZZLE))


def test_no_pressure_no_jet():
    assert exit_velocity(0, WATER, IMPACT_NOZZLE) == 0


def test_capsule_pressure_drops_like_boyles_law():
    cap = Capsule(volume=ml(20), fluid_volume=ml(10), pressure_psi=30)
    assert capsule_pressure(cap, 0) == pytest.approx(30 * PSI)
    # doubling the air volume halves the absolute pressure
    p_abs = (30 * PSI + 101325) / 2
    assert capsule_pressure(cap, ml(10)) == pytest.approx(p_abs - 101325)


def test_fire_never_uses_more_fluid_than_loaded():
    cap = Capsule(volume=ml(20), fluid_volume=ml(5), pressure_psi=60)
    used, _ = fire(cap, WATER, IMPACT_NOZZLE, 10.0)
    assert used <= ml(5)


def test_can_needs_more_than_static_threshold():
    tip_f, _ = can_static_thresholds()
    weak = [(i * 1e-3, 0, tip_f * 0.9) for i in range(500)]
    strong = [(i * 1e-3, 0, tip_f * 1.2) for i in range(500)]
    assert can_response(weak) != "tips"
    assert can_response(strong) == "tips"


def test_short_hard_hit_with_enough_impulse_tips_can():
    j = impulse_to_tip()
    hit = [(i * 1e-3, 0, j * 1.1 / 5e-3) for i in range(5)]   # 5 ms hammer blow
    assert can_response(hit) == "tips"


def test_wide_short_tube_beats_long_thin_tube():
    p = 30 * PSI
    thin = exit_velocity(p, ALGINATE_1PCT, IMPACT_NOZZLE, Plumbing(3e-3, 0.15))
    wide = exit_velocity(p, ALGINATE_1PCT, IMPACT_NOZZLE, Plumbing(5e-3, 0.08))
    assert wide > thin


def test_brief_spike_does_not_push_can():
    _, slide_f = can_static_thresholds()
    spike = [(0, 0, slide_f * 1.05)]
    assert can_response(spike) == "stays"
