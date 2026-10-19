"""Render preview PNGs of the model (no CAD program needed).

    python render_preview.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cadquery as cq

import webshooter_cad as m

OUT = Path(__file__).parent / "preview"


def mesh(wp, offset=(0, 0, 0)):
    verts, tris = wp.val().tessellate(0.3)
    ox, oy, oz = offset
    pts = [(v.x + ox, v.y + oy, v.z + oz) for v in verts]
    return [[pts[i] for i in t] for t in tris]


def draw(items, path, elev=25, azim=-60, title=""):
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(projection="3d")
    allpts = []
    for wp, offset, color, alpha in items:
        faces = mesh(wp, offset)
        # model Y is "up"; plot it on the vertical axis
        faces = [[(x, z, y) for x, y, z in f] for f in faces]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=0,
                                             alpha=alpha, shade=True))
        allpts += [p for f in faces for p in f]
    for i, setter in enumerate((ax.set_xlim, ax.set_ylim, ax.set_zlim)):
        vals = [p[i] for p in allpts]
        setter(min(vals), max(vals))
    ax.set_box_aspect([max(p[i] for p in allpts) - min(p[i] for p in allpts) for i in range(3)])
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    deck = m.WRIST_HEIGHT / 2 + m.WALL + m.PLATFORM_THICK
    r_out = m.CAPSULE_DIA / 2 + m.CLIP_WALL
    capsule_y = deck + m.CAPSULE_DIA / 2 + 1
    bracer = m.bracer()
    items = [(bracer, (0, 0, 0), "#c0392b", 1.0)]
    for x in (-(r_out + 1), r_out + 1):
        items.append((m.capsule_placeholder(), (x, capsule_y, -4), "#7fb3ff", 0.6))
    items.append((m.tray_lid(), (0, deck + m.TRAY_DEPTH + 1, m.BRACER_LENGTH - m.TRAY_LENGTH / 2 - 2),
                  "#333344", 1.0))
    draw(items, OUT / "assembly.png", title="Web shooter v0: bracer + capsules (blue, not printed)")
    draw([(bracer, (0, 0, 0), "#c0392b", 1.0)], OUT / "bracer_front.png", elev=10, azim=-90,
         title="Bracer, looking down the forearm")
    draw([(m.palm_pad(), (0, 0, 0), "#333344", 1.0)], OUT / "palm_pad.png", elev=50, azim=-60,
         title="Palm pad: trigger pocket + thumb-side tether button")
    print(f"previews in {OUT}")


if __name__ == "__main__":
    main()
