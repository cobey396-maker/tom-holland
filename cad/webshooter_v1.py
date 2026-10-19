"""Web shooter v1: minimal, low-profile wrist unit.

Based on the early Tinkercad prototype (reference/early_prototype.obj):
same layout -- nozzles toward the hand, round screen in the middle, capsules
behind -- resized around real parts and a real wrist.

    python webshooter_v1.py

Axes: X = across the wrist, Y = up (away from the skin), Z = along the forearm
(Z = 0 is the hand end).
"""
from pathlib import Path
import cadquery as cq

# ------------------------------------------------------------------ PARAMETERS (mm)
# wrist (measure over your sleeve, ~3 cm back from the wrist bone)
WRIST_WIDTH = 62
WRIST_HEIGHT = 45

# two slim C-shaped bands, open on the side opposite the pod so they slip on,
# each closed with one strap. The front band sits just behind the wrist joint.
CUFF_WALL = 2.4
FRONT_BAND = 28
REAR_BAND = 20
CUFF_GAP = 34             # opening on the far side
STRAP_WIDTH = 20
STRAP_SLOT = 3.2

# round display: 1.28" GC9A01 module (36 mm round board, 32 mm glass)
SCREEN_BOARD_DIA = 36.5
SCREEN_BOARD_DEPTH = 4.0
SCREEN_BOSS_DIA = 40

# electronics under the screen: XIAO ESP32-C3 (21 x 17.5) stacked on a small LiPo
BAY = (27, 23, 9)         # x, z, depth

# capsules: two slim pressure-rated tubes with a sliding piston inside
CAPSULE_OD = 14
CAPSULE_LENGTH = 60
CLIP_WALL = 1.8
CLIP_OPENING = 10.5

# front block: two micro valves + the two nozzles (string coax, impact)
FRONT_LENGTH = 20
FRONT_HEIGHT = 13
VALVE_POCKET = (30, 14, 9)   # x, z, height
COAX_HOLE = 8.2
IMPACT_HOLE = 7.2

POD_FLOOR = 2.0
BUTTON_POCKET_DEPTH = 3.6     # 12 x 12 x 3.5 mm tactile switch body

# palm pad: two buttons side by side in the palm, like the early prototype's two round tips.
# Held by an elastic loop around the hand; a thin flexible cable runs back to the band,
# so the wrist can still bend freely.
PALM_PAD = (48, 24, 7.5)      # length across the palm, width, thickness
PALM_BUTTON = 12.3            # 12 mm tactile switches
BUTTON_SPACING = 20
TETHER_RECESS = 1.2           # tether button sits lower so it isn't pressed by accident
LOOP_SLOT = (2.6, 16)         # elastic loop slots at each end
CABLE = (6, 1.8)              # flat cable channel on the underside

OUT = Path(__file__).parent


def _ellipse(w, h, length, z0=0.0):
    return cq.Workplane("XY").ellipse(w / 2, h / 2).extrude(length).translate((0, 0, z0))


def layout():
    """Z positions of each section along the pod."""
    screen_z0 = FRONT_LENGTH
    capsule_z0 = screen_z0 + SCREEN_BOSS_DIA
    end = capsule_z0 + CAPSULE_LENGTH + 4
    return screen_z0, capsule_z0, end


def wearer_hollow(length):
    return _ellipse(WRIST_WIDTH, WRIST_HEIGHT, length + 2, -1)


def band(z0, length):
    a, b = WRIST_WIDTH / 2, WRIST_HEIGHT / 2
    ring = (_ellipse(WRIST_WIDTH + 2 * CUFF_WALL, WRIST_HEIGHT + 2 * CUFF_WALL, length, z0)
            .cut(_ellipse(WRIST_WIDTH, WRIST_HEIGHT, length, z0)))
    gap = (cq.Workplane("XY").box(CUFF_GAP, 20, length + 2, centered=(True, True, False))
           .translate((0, -b - 5, z0 - 1)))
    ring = ring.cut(gap)
    # one strap slot on each side, next to the opening
    strap = min(STRAP_WIDTH, length - 6)
    for side in (-1, 1):
        slot = (cq.Workplane("XY").box(12, STRAP_SLOT, strap + 1)
                .translate((side * (a - 2), -b * 0.45, z0 + length / 2)))
        ring = ring.cut(slot)
    return ring


def cuff():
    _, _, end = layout()
    return band(0, FRONT_BAND).union(band(end - REAR_BAND, REAR_BAND))


def pod():
    b = WRIST_HEIGHT / 2
    deck = b + CUFF_WALL                       # top of the cuff
    screen_z0, capsule_z0, end = layout()
    width = 2 * (CAPSULE_OD + 2 * CLIP_WALL) + 1

    # floor that hugs the cuff
    floor = (cq.Workplane("XY").box(width, POD_FLOOR + 6, end, centered=(True, False, False))
             .translate((0, deck - 6, 0)))
    body = floor.cut(wearer_hollow(end))
    top = deck + POD_FLOOR

    # front: valve pocket + nozzles. Ends flush with the wrist so it never blocks the hand.
    front = (cq.Workplane("XY").box(width, FRONT_HEIGHT, FRONT_LENGTH, centered=(True, False, False))
             .translate((0, top, 0)).edges("|Z and >Y").fillet(4))
    # open at the top so the valves drop in; a snap lid closes it later
    vp = (cq.Workplane("XY").box(VALVE_POCKET[0], FRONT_HEIGHT + 1, VALVE_POCKET[1],
                                 centered=(True, False, False))
          .translate((0, top + FRONT_HEIGHT - VALVE_POCKET[2], FRONT_LENGTH - VALVE_POCKET[1] - 1.5)))
    nozzles = (cq.Workplane("XY").pushPoints([(-8, top + FRONT_HEIGHT / 2 + 1)]).circle(COAX_HOLE / 2)
               .extrude(8).translate((0, 0, -1))
               .union(cq.Workplane("XY").pushPoints([(8, top + FRONT_HEIGHT / 2 + 1)])
                      .circle(IMPACT_HOLE / 2).extrude(8).translate((0, 0, -1))))
    body = body.union(front).cut(vp).cut(nozzles)

    # screen boss with the electronics bay underneath
    cz = screen_z0 + SCREEN_BOSS_DIA / 2
    boss_h = BAY[2] + SCREEN_BOARD_DEPTH + 1
    boss = (cq.Workplane("XZ").circle(SCREEN_BOSS_DIA / 2).extrude(-boss_h)
            .translate((0, top, cz)))
    board = (cq.Workplane("XZ").circle(SCREEN_BOARD_DIA / 2).extrude(-SCREEN_BOARD_DEPTH - 1)
             .translate((0, top + boss_h - SCREEN_BOARD_DEPTH, cz)))
    bay = (cq.Workplane("XY").box(BAY[0], BAY[2] + 1, BAY[1], centered=(True, False, True))
           .translate((0, top + 0.01, cz)))
    usb = cq.Workplane("XY").box(12, 5, 10).translate((width / 2, top + 3, cz))       # USB-C charge port
    wires = cq.Workplane("XY").box(8, 5, FRONT_LENGTH).translate((0, top + 2.5, cz - SCREEN_BOSS_DIA / 2))
    body = body.union(boss).cut(board).cut(bay).cut(usb).cut(wires)

    # twin capsule clips
    r = CAPSULE_OD / 2
    r_out = r + CLIP_WALL
    for x in (-(r_out + 0.5), r_out + 0.5):
        cy = top + r + 0.3
        clip = cq.Workplane("XY").circle(r_out).extrude(CAPSULE_LENGTH).translate((x, cy, capsule_z0))
        web = (cq.Workplane("XY").box(2 * r_out, r, CAPSULE_LENGTH, centered=(True, False, False))
               .translate((x, top, capsule_z0)))
        bore = cq.Workplane("XY").circle(r + 0.2).extrude(CAPSULE_LENGTH + 2).translate((x, cy, capsule_z0 - 1))
        mouth = (cq.Workplane("XY").box(CLIP_OPENING, r_out, CAPSULE_LENGTH + 2, centered=(True, False, False))
                 .translate((x, cy + r * 0.6, capsule_z0 - 1)))
        body = body.union(clip.union(web)).cut(bore).cut(mouth)
    return body


def palm_pad():
    """Two-button palm pad: FIRE (tap = impact, hold = string) and TETHER."""
    l, w, t = PALM_PAD
    pad = (cq.Workplane("XY").slot2D(l, w).extrude(t)
           .edges(">Z").fillet(2.2))
    # FIRE: flush, under the middle/ring fingers
    d = BUTTON_POCKET_DEPTH
    fire = (cq.Workplane("XY").box(PALM_BUTTON, PALM_BUTTON, d + 1, centered=(True, True, False))
            .translate((-BUTTON_SPACING / 2, 0, t - d)))
    # TETHER: recessed, with a raised ring you can find by feel
    tether = (cq.Workplane("XY").box(PALM_BUTTON, PALM_BUTTON, d + TETHER_RECESS + 1, centered=(True, True, False))
              .translate((BUTTON_SPACING / 2, 0, t - d - TETHER_RECESS)))
    ring = (cq.Workplane("XY").circle(PALM_BUTTON / 2 + 3).circle(PALM_BUTTON / 2 + 1.6).extrude(1.2)
            .translate((BUTTON_SPACING / 2, 0, t)))
    pad = pad.union(ring).cut(fire).cut(tether)
    # wire holes from each button pocket down into the cable channel
    for x in (-BUTTON_SPACING / 2, BUTTON_SPACING / 2):
        pad = pad.cut(cq.Workplane("XY").circle(1.6).extrude(t).translate((x, 0, 0)))
    # cable channel underneath, exiting toward the wrist (-Y)
    channel = (cq.Workplane("XY").box(BUTTON_SPACING + CABLE[0], CABLE[0], CABLE[1], centered=(True, True, False))
               .union(cq.Workplane("XY").box(CABLE[0], w, CABLE[1], centered=(True, False, False))
                      .translate((0, -w, 0))))
    pad = pad.cut(channel)
    # elastic loop slots at both ends
    for side in (-1, 1):
        pad = pad.cut(cq.Workplane("XY").box(LOOP_SLOT[0], LOOP_SLOT[1], t * 3)
                      .translate((side * (l / 2 - 4.5), 0, 0)))
    return pad


def cable_clip():
    """Snaps onto the front band's edge to hold the palm cable."""
    return (cq.Workplane("XY").box(10, 8, 4).cut(cq.Workplane("XY").box(10.2, CUFF_WALL + 0.3, 2.6)
                                                  .translate((0, 0, -0.8)))
            .cut(cq.Workplane("XY").box(CABLE[0] + 0.4, 9, CABLE[1] + 0.3).translate((0, 0, 1.2))))


def unit():
    return cuff().union(pod())


def capsule_placeholder():
    return cq.Workplane("XY").circle(CAPSULE_OD / 2).extrude(CAPSULE_LENGTH + 6)


def main():
    u = unit()
    (OUT / "stl").mkdir(exist_ok=True)
    cq.exporters.export(u, str(OUT / "stl" / "v1_wrist_unit.stl"), tolerance=0.05)
    pad = palm_pad()
    cq.exporters.export(pad, str(OUT / "stl" / "v1_palm_pad.stl"), tolerance=0.05)
    cq.exporters.export(cable_clip(), str(OUT / "stl" / "v1_cable_clip.stl"), tolerance=0.05)
    pb = pad.val().BoundingBox()
    print(f"palm pad: {pb.xlen:.0f} x {pb.ylen:.0f} x {pb.zlen:.1f} mm, valid={pad.val().isValid()}")
    bb = u.val().BoundingBox()
    deck = WRIST_HEIGHT / 2 + CUFF_WALL
    print(f"wrist unit: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm, "
          f"{bb.ymax - deck:.1f} mm tall above the cuff, {u.val().Volume() / 1000:.1f} cm^3, "
          f"valid={u.val().isValid()}, solids={len(u.solids().vals())}")


if __name__ == "__main__":
    main()
