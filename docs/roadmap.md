# Roadmap

Target: working demo by **mid-November 2026**.

## Phase 0 — $0, start now
- [ ] Brainstorm and decide core design questions ([brainstorm.md](brainstorm.md))
- [ ] Email 2–3 NCAT faculty (chemistry / chemical engineering / bioengineering) about lab access for Phase 4
- [ ] Ask the makerspace if they stock free/consumable parts (syringes, electronics, filament)
- [ ] Python simulation: jet trajectory + range vs. pressure and needle size
- [ ] Write pump/trigger firmware and test it in the free [Wokwi](https://wokwi.com) ESP32 simulator
- [ ] Sketch the wrist housing in Tinkercad or Onshape (both free)
- [ ] Build the video-analysis script and test it on sample footage

## Phase 1 — bench rig (~$35)
- [ ] Buy alginate, calcium chloride, syringes, blunt needles, luer fittings
- [ ] Build DIY coaxial needle
- [ ] First fibers by hand-pushing syringes; film in slow-mo

## Phase 2 — motorized + data (~$35)
- [ ] ESP32 + stepper syringe pump on a breadboard (no soldering)
- [ ] Parameter sweep: concentration × flow rate × needle gauge
- [ ] Auto-measure every shot with OpenCV, log to CSV, plot results

## Phase 3 — wrist prototype
- [ ] Book NCAT makerspace slot, print housing
- [ ] Integrate pump, trigger, battery
- [ ] Demo video + final writeup

## Phase 4 — the real web
- [ ] Replicate silk/dopamine fibers in a faculty lab
