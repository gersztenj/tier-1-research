"""
Consolidate the think-tank's data sources into a single `site/data.js` that the
website loads (via <script src>, so it works on file:// and any static host).

Inputs : radar/radar_data.json, notes/notes_index.json, scorecard/scorecard.json
Output : site/data.js  (window.TANK = {...})

Run after refreshing the radar or publishing a note:
    python site/build_site_data.py
"""
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(rel, default):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    radar = load("radar/radar_data.json", {"items": [], "count": 0, "open_comment_count": 0,
                                            "agency_counts": {}, "generated_at": None})
    notes = load("notes/notes_index.json", {"notes": []})
    scorecard = load("scorecard/scorecard.json", {})

    published = [n for n in notes.get("notes", []) if n.get("status") == "published"]

    # Live scorecard numbers (derived, so they can't drift from reality).
    cites_total = sum(n.get("citations_total", 0) for n in published)
    cites_verified = sum(n.get("citations_verified", 0) for n in published)
    derived = {
        "proposals_tracked": radar.get("count", 0),
        "open_comment_windows": radar.get("open_comment_count", 0),
        "notes_published": len(published),
        "citations_total": cites_total or scorecard.get("citations_total", 0),
        "citations_verified": cites_verified or scorecard.get("citations_verified", 0),
        "launched": scorecard.get("launched"),
        "radar_updated": radar.get("generated_at"),
    }

    tank = {
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "radar": radar,
        "notes": published,
        "scorecard": {**scorecard, **derived},
    }

    out = os.path.join(HERE, "data.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("window.TANK = ")
        json.dump(tank, f, ensure_ascii=False, indent=1)
        f.write(";\n")
    print(f"Wrote {out}")
    print(f"  radar: {derived['proposals_tracked']} proposals "
          f"({derived['open_comment_windows']} open) · notes: {derived['notes_published']}")


if __name__ == "__main__":
    main()
