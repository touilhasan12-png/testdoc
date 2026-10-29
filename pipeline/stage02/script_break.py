#!/usr/bin/env python3
"""SUBSTITUTE for scriptbreak (no repository under that name).
Turns each scene into shots with an explicit source plan: which tool produces the image, and
which disclosure label is burned in. The shot list is what stage 4-11 consume."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage02"

def main():
    out = out_dir(STAGE)
    scenes = json.load(open(os.path.join(out, "scenes.json")))["scenes"]
    shots = []
    n = 0
    for s in scenes:
        plan = {
            "COLD":        [("OpenMontage", "4K ocean plate from Archive.org", "ARCHIVAL PHOTO"),
                            ("Remotion", "title overlay 00:22-00:30", "GRAPHIC")],
            "SHIP-1":      [("Pallaidium/Blender blockout", "deck + sail + wheel", "REENACTMENT"),
                            ("AI-Forensics-3D", "camera move across deck", "REENACTMENT")],
            "SHIP-2":      [("Pallaidium/Blender blockout", "cabin props, no people", "REENACTMENT")],
            "EVID-1":      [("Loc page image + Real-ESRGAN", "newspaper column 1873-03-14", "ARCHIVAL PHOTO"),
                            ("ScanOld", "detail crop, re-set as clipping", "RE-CREATED PROP")],
            "EVID-2":      [("text-to-handwriting", "logbook page, entries stop", "RE-CREATED PROP"),
                            ("synthetic-manuscript-generator", "ink and fold ageing", "RE-CREATED PROP")],
            "HEAR-1":      [("broll-fetcher/OpenMontage", "Gibraltar harbour plate", "ARCHIVAL PHOTO"),
                            ("QGIS+kepler.gl", "approach route map", "GRAPHIC")],
            "FICT-1":      [("ScanOld", "Cornhill Magazine cover, re-created", "RE-CREATED PROP"),
                            ("text-to-handwriting", "handwritten manuscript page", "RE-CREATED PROP")],
            "FICT-2":      [("Remotion", "Marie/Mary spelling cascade", "GRAPHIC")],
            "SHIP-3":      [("Pallaidium/Blender blockout", "empty davits, no boat", "REENACTMENT"),
                            ("ScanOld", "sailmaker's note, re-created", "RE-CREATED PROP")],
            "CODA-2":      [("Remotion", "list of absent details", "GRAPHIC")],
            "CODA":        [("OpenMontage", "empty horizon plate", "ARCHIVAL PHOTO"),
                            ("Remotion", "end card + credits", "GRAPHIC")],
        }[s["slug"]]
        for tool, what, label in plan:
            n += 1
            shots.append({"shot": f"S{n:02d}", "scene": s["slug"], "tool": tool, "asset": what,
                          "label": label if label != "ARCHIVAL PHOTO" else s["on_screen_label"].split(" (")[0]})
    json.dump(shots, open(os.path.join(out, "shotlist.json"), "w"), indent=1)
    csv = ["shot,scene,tool,asset,on_screen_label"]
    for s in shots:
        csv.append(f"{s['shot']},{s['scene']},{s['tool']},\"{s['asset']}\",{s['label']}")
    open(os.path.join(out, "shotlist.csv"), "w").write("\n".join(csv) + "\n")
    log(STAGE, "scriptbreak(SUBSTITUTED)", f"{len(shots)} shots planned across {len(scenes)} scenes")
    print(json.dumps({"shots": len(shots)}))

if __name__ == "__main__":
    main()
