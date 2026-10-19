"""Parametric 3D model of the web shooter (concept v0).

Change the numbers in PARAMETERS (especially wrist size) and rerun:

    python webshooter_cad.py

Writes one STL per printable part to stl/ and a full assembly to webshooter_v0.step
(STEP opens in Onshape / Fusion; STL opens in Tinkercad and the makerspace slicer).

NOTE: the pressurized capsules are NOT printed. 3D prints are porous and can split
under pressure. The capsules are off-the-shelf pressure-rated tubes; this model only
holds them.
"""
from pathlib import Path
import cadquery as cq

# ------------------------------------------------------------------ PARAMETERS (mm)
WRIST_WIDTH = 62          # side to side, measured over a sleeve
WRIST_HEIGHT = 45         # top to bottom
WALL = 3.0                # bracer shell thickness
BRACER_LENGTH = 130       # along the forearm
COVERAGE_CUT = 4          # keep the shell above this height (wraps a bit past halfway)

STRAP_WIDTH = 25          # velcro strap
STRAP_SLOT_GAP = 3.5

PLATFORM_WIDTH = 64
PLATFORM_THICK = 4

CAPSULE_DIA = 22          # outside diameter of the pressure-rated capsule tube
CAPSULE_LENGTH = 70       # length of the clip holding each capsule
CLIP_WALL = 2.6
CLIP_OPENING = 17         # gap at the top so the capsule snaps in

TRAY_LENGTH = 50          # electronics tray behind the capsules
TRAY_INNER = (56, 32)     # ESP32 dev board ~52 x 28
TRAY_DEPTH = 16

NOZZLE_BLOCK = (40, 18, 14)   # width, height, depth
COAX_HOLE = 8.2               # holds the coaxial needle assembly (string mode)
IMPACT_HOLE = 7.2             # holds the 5 mm ID / 7 mm OD impact tube

PALM_PAD = (34, 28, 7)        # palm switch pad
BUTTON = 12.3                 # 12 mm tactile switch pocket (palm trigger)
SIDE_BUTTON = 6.3             # 6 mm tactile switch pocket (tether button)

OUT = Path(__file__).parent


# ------------------------------------------------------------------ parts
def ellipse_prism(w, h, length):
    return cq.Workplane("XY").ellipse(w / 2, h / 2).extrude(length)


def bracer():
    a_in, b_in = WRIST_WIDTH / 2, WRIST_HEIGHT / 2
    shell = (ellipse_prism(WRIST_WIDTH + 2 * WALL, WRIST_HEIGHT + 2 * WALL, BRACER_LENGTH)
             .cut(ellipse_prism(WRIST_WIDTH, WRIST_HEIGHT, BRACER_LENGTH)))
    # keep the top part of the shell; the bottom stays open so it slips on
    keep = cq.Workplane("XY").box(200, 200, BRACER_LENGTH, centered=(True, False, False)) \
        .translate((0, COVERAGE_CUT - b_in, 0))
    shell = shell.intersect(keep)

    # flat platform on top for the hardware
    top = b_in + WALL
    platform = (cq.Workplane("XY")
                .box(PLATFORM_WIDTH, PLATFORM_THICK + 6, BRACER_LENGTH, centered=(True, False, False))
                .translate((0, top - 6, 0))
                .cut(ellipse_prism(WRIST_WIDTH, WRIST_HEIGHT, BRACER_LENGTH)))
    body = shell.union(platform)

    # strap slots through both side walls, near the front and the back
    # (at this height the middle is the hollow for the arm, so only the walls get cut)
    for z in (22, BRACER_LENGTH - 22):
        slot = cq.Workplane("XY").box(WRIST_WIDTH + 4 * WALL + 10, STRAP_SLOT_GAP, STRAP_WIDTH + 1) \
            .translate((0, COVERAGE_CUT - b_in + 9, z))
        body = body.cut(slot)

    deck = top + PLATFORM_THICK
    # two capsule clips side by side at the front
    r_out = CAPSULE_DIA / 2 + CLIP_WALL
    for x in (-(r_out + 1), r_out + 1):
        clip = (cq.Workplane("XY").circle(r_out).extrude(CAPSULE_LENGTH)
                .translate((x, deck + CAPSULE_DIA / 2 + 1, 6)))
        base = (cq.Workplane("XY").box(2 * r_out, CAPSULE_DIA / 2 + 1, CAPSULE_LENGTH,
                                       centered=(True, False, False))
                .translate((x, deck, 6)))
        bore = (cq.Workplane("XY").circle(CAPSULE_DIA / 2 + 0.2).extrude(CAPSULE_LENGTH + 2)
                .translate((x, deck + CAPSULE_DIA / 2 + 1, 5)))
        opening = (cq.Workplane("XY").box(CLIP_OPENING, r_out, CAPSULE_LENGTH + 2,
                                          centered=(True, False, False))
                   .translate((x, deck + CAPSULE_DIA / 2 + 1 + CAPSULE_DIA / 2 * 0.55, 5)))
        body = body.union(clip.union(base)).cut(bore).cut(opening)

    # electronics tray at the back
    tw, tl = TRAY_INNER[0] + 2 * 2, TRAY_LENGTH
    tray = (cq.Workplane("XY").box(tw, TRAY_DEPTH, tl, centered=(True, False, False))
            .translate((0, deck, BRACER_LENGTH - tl - 2)))
    pocket = (cq.Workplane("XY").box(TRAY_INNER[0], TRAY_DEPTH, TRAY_INNER[1] + 12,
                                     centered=(True, False, False))
              .translate((0, deck + 2, BRACER_LENGTH - tl + 1)))
    wire_hole = (cq.Workplane("XY").box(10, 6, 8).translate((0, deck + 6, BRACER_LENGTH - tl - 2)))
    body = body.union(tray).cut(pocket).cut(wire_hole)

    # nozzle block on the front edge, sticking out past the wrist
    nw, nh, nd = NOZZLE_BLOCK
    block = (cq.Workplane("XY").box(nw, nh, nd, centered=(True, False, False))
             .translate((0, deck, -nd + 6)))
    coax = cq.Workplane("XY").circle(COAX_HOLE / 2).extrude(nd + 2).translate((-9, deck + nh / 2, -nd + 5))
    impact = cq.Workplane("XY").circle(IMPACT_HOLE / 2).extrude(nd + 2).translate((9, deck + nh / 2, -nd + 5))
    body = body.union(block).cut(coax).cut(impact)
    return body


def tray_lid():
    tw = TRAY_INNER[0] + 2 * 2
    lid = cq.Workplane("XY").box(tw, 2, TRAY_LENGTH - 2)
    lip = cq.Workplane("XY").box(TRAY_INNER[0] - 0.4, 3, TRAY_INNER[1] + 11.6).translate((0, -2.5, 0))
    switch_hole = cq.Workplane("XY").box(13, 10, 8).translate((tw / 4, 0, TRAY_LENGTH / 4))  # arm/safe toggle
    led_hole = cq.Workplane("XY").circle(2.6).extrude(10, both=True) \
        .rotate((0, 0, 0), (1, 0, 0), 90).translate((-tw / 4, 0, TRAY_LENGTH / 4))
    return lid.union(lip).cut(switch_hole).cut(led_hole)


def palm_pad():
    w, l, t = PALM_PAD
    pad = cq.Workplane("XY").box(w, l, t).edges("|Z").fillet(6).edges(">Z").fillet(2)
    pocket = cq.Workplane("XY").box(BUTTON, BUTTON, 4).translate((0, 0, t / 2 - 1.5))
    side = cq.Workplane("XY").box(SIDE_BUTTON, 4, SIDE_BUTTON).translate((0, -l / 2 + 1.5, 0))  # thumb side
    wires = cq.Workplane("XY").box(4, l, 2.5).translate((0, l / 4, -t / 2 + 2))
    slots = (cq.Workplane("XY").box(3, 18, t + 2).translate((w / 2 - 4, 0, 0))
             .union(cq.Workplane("XY").box(3, 18, t + 2).translate((-w / 2 + 4, 0, 0))))
    return pad.cut(pocket).cut(side).cut(wires).cut(slots)


def capsule_placeholder():
    """Not printed: shows where the pressure-rated capsule sits."""
    return cq.Workplane("XY").circle(CAPSULE_DIA / 2).extrude(CAPSULE_LENGTH + 20)


# ------------------------------------------------------------------ build
def main():
    parts = {"bracer": bracer(), "tray_lid": tray_lid(), "palm_pad": palm_pad()}
    (OUT / "stl").mkdir(exist_ok=True)
    for name, part in parts.items():
        cq.exporters.export(part, str(OUT / "stl" / f"{name}.stl"), tolerance=0.05)
        bb = part.val().BoundingBox()
        print(f"{name:<9} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm")

    b_in = WRIST_HEIGHT / 2
    deck = b_in + WALL + PLATFORM_THICK
    r_out = CAPSULE_DIA / 2 + CLIP_WALL
    assy = cq.Assembly(name="webshooter_v0")
    assy.add(parts["bracer"], name="bracer", color=cq.Color(0.75, 0.1, 0.1))
    assy.add(parts["tray_lid"], name="tray_lid", color=cq.Color(0.2, 0.2, 0.25),
             loc=cq.Location((0, deck + TRAY_DEPTH + 1, BRACER_LENGTH - TRAY_LENGTH / 2 - 2)))
    for i, x in enumerate((-(r_out + 1), r_out + 1)):
        assy.add(capsule_placeholder(), name=f"capsule_{i}", color=cq.Color(0.6, 0.8, 1.0, 0.6),
                 loc=cq.Location((x, deck + CAPSULE_DIA / 2 + 1, -4)))
    assy.add(parts["palm_pad"], name="palm_pad", color=cq.Color(0.2, 0.2, 0.25),
             loc=cq.Location((0, -10, -70)))
    assy.export(str(OUT / "webshooter_v0.step"))
    print("wrote stl/*.stl and webshooter_v0.step")


if __name__ == "__main__":
    main()
