#!/usr/bin/env python3
"""Import a TrainHeroic training_data.csv export into this workout program.

Privacy: this script reads ONLY training_data.csv (workout history). It never
reads or copies profile, message, readiness, nutrition, or team files from a
TrainHeroic GDPR export. The jennyrdh/Fitness repo is public — do not point
this script at those other CSVs.

Usage:
  python scripts/import_trainheroic.py \\
      --input /path/to/training_data.csv \\
      --program-dir /path/to/workout-program \\
      --recent-logs-since 2026-09-01
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


EMPTY_DATA = {
    "",
    "x",
    "rep x",
    "rep x pound",
    "rep x  pound",
    "rpe x",
    "time x",
    "second x",
    "rpe x time",
    "time x pound",
    "time x time",
    "rep x rep",
}

INSTRUCTIONAL_TITLES = {
    "how to warm up",
    "what are myo sets?",
    "what are pyramid sets? (dral)",
}

# Program working-weight keys -> TrainHeroic exercise names, most preferred first.
# related = close variations used to fill context, never invented loads.
EXERCISE_MAP = {
    "back_squat": {
        "candidates": ["Back Squat", "Barbell Back Squat", "BB Back Squat (Quads)"],
        "related": ["Hack Squat", "Smith machine squat"],
    },
    "leg_press": {
        "candidates": ["Leg Press (quads)", "Leg Press (glutes)", "Leg Press (adductor)"],
        "related": [
            "SL Leg Press (Glutes)",
            "SL Leg Press (Quads)",
            "Leg Press (Glutes) (Double Pump)",
            "Sissy Leg Press (reverse banded)",
        ],
    },
    "leg_extension": {
        "candidates": ["Leg Extensions", "Alternating Leg Extension", "10-6-10 Leg Extension"],
        "related": [],
    },
    "leg_curl": {
        "candidates": [
            "SL Seated Ham Curl",
            "Seated Hamstring Curls",
            "Lying Hamstring Curl",
            "Alternating Lying Leg Curl",
        ],
        "related": ["Seated Hamstring Curls", "Lying Hamstring Curl"],
    },
    "standing_calf_raise": {
        "candidates": ["Standing Calf Raise Machine", "Standing Calf Raise"],
        "related": ["Calf Raise (leg press)"],
    },
    "barbell_bench_press": {
        "candidates": ["Flat BB Press", "Close Grip Bench Press", "Close grip bench"],
        "related": ["Chest Press Machine", "Flat DB Press"],
    },
    "overhead_press": {
        "candidates": ["Barbell Overhead Press", "Shoulder Press", "SA Overhead Press"],
        "related": ["Shoulder press machine"],
    },
    "incline_db_bench": {
        "candidates": [
            "Incline DB Press (60 degree)",
            "Incline DB Press (45 Degree)",
            "Incline DB Press (15 degree)",
            "Incline DB Bench Press",
        ],
        "related": ["Incline smith machine press"],
    },
    "lateral_raise": {
        "candidates": [
            "DB Lateral Raises",
            "SA behind the back lateral raise",
            "Hand height cable lateral raise",
            "DB Lateral Raise (seated)",
            "Lying DB Lateral Raise",
        ],
        "related": ["SA Cable Y Raise"],
    },
    "overhead_triceps_extension": {
        "candidates": [
            "OH Tricep Ext (DB)",
            "SA OH Tricep Ext (cable)",
            "Overhead cable tricep extension",
            "DB Skullcrusher",
            "EZ Bar Skullcrusher",
        ],
        "related": [],
    },
    "triceps_pushdown": {
        "candidates": ["Tricep Pushdown", "SA Tricep Pushdown", "Band Tricep Pushdown"],
        "related": ["Cross Cable Tricep Ext"],
    },
    "romanian_deadlift": {
        "candidates": ["RDL (Romanian Deadlift)", "RDL", "Stiff-Leg RDL"],
        "related": ["B-Stance RDL", "Bent-knee RDL"],
    },
    "hip_thrust": {
        "candidates": ["BB Hip Thrust", "Dead Stop Hip Thrust", "B-Stance Hip thrust"],
        "related": ["BB Glute Bridge"],
    },
    "step_up_or_reverse_lunge": {
        "candidates": [
            "FFE Reverse Lunge",
            "Walking Lunges",
            "Front Foot Elevated Split Squat",
        ],
        "related": [],
    },
    "back_extension": {
        "candidates": [
            "45 Degree hip extension",
            "45 Degree Hip Extension (band)",
            "Back Extension",
            "1.5 Rep 45 Degree Hip Extension",
        ],
        "related": [],
    },
    "barbell_or_chest_supported_row": {
        "candidates": [
            "Chest supported row machine (Elbows flared)",
            "Chest Supported Row Machine (neutral grip)",
            "Chest supported T-bar row (Elbows tucked)",
            "Chest supported T-Bar Row (Elbows flared)",
            "Bent Over Row (BB/DB)",
        ],
        "related": ["Chest Supported DB Row (Elbows flared)"],
    },
    "chinup_or_lat_pulldown": {
        "candidates": [
            "Close Grip Pulldown",
            "Wide grip pulldown",
            "Supinated Pulldown",
            "SA Lat Pulldown (seated)",
            "Lat Pulldown",
            "Lat Pull Downs",
            "Pull-Up",
            "Pull-up",
            "Pull-ups (+ Band-assisted options)",
            "Assisted Pull-ups",
        ],
        "related": ["Pull-Up", "Pull-up", "Assisted Pull-ups"],
    },
    "single_arm_row": {
        "candidates": ["SA DB Row"],
        "related": [],
    },
    "straight_arm_lat_pulldown": {
        "candidates": ["DB Pullovers", "Cable Pullover"],
        "related": [],
    },
    "rear_delt_fly": {
        "candidates": [
            "Rear Delt Cable Fly (+SA Version)",
            "Rear delt pec deck fly",
            "SA Rear Delt Fly",
            "SA Rear Delt Pec Deck Fly",
            "Cable face pull",
        ],
        "related": [],
    },
    "ez_bar_or_db_curl": {
        "candidates": [
            "Incline DB Curls",
            "DB Hammer Curls",
            "EZ Bar Curls",
            "Alternating DB Curl",
        ],
        "related": ["Lazy Man Cable Curl", "Cable curls"],
    },
    "front_squat": {
        "candidates": ["Goblet Squat", "Goblet squat", "Goblet Squats (Heels Elevated)"],
        "related": [],
    },
    "bulgarian_split_squat": {
        "candidates": [
            "Bulgarian Split Squat",
            "Step back bulgarians",
            "RFE Split Squats (Glutes)",
            "RFE Split Squat (Quads)",
            "Split Squat (quads)",
        ],
        "related": [],
    },
    "single_leg_rdl": {
        "candidates": ["Single Leg RDL", "B-Stance RDL"],
        "related": [],
    },
    "seated_calf_raise": {
        "candidates": ["Seated Calf Raise"],
        "related": ["Calf Raise (leg press)"],
    },
}

PII_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PII_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s])\d{3}[-.\s]\d{4}\b")


def parse_num_list(s: str) -> list[int | float]:
    vals: list[int | float] = []
    if not s:
        return vals
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"[-+]?\d+(?:\.\d+)?", part)
        if not m:
            continue
        v = float(m.group(0))
        vals.append(int(v) if v == int(v) else v)
    return vals


def normalize_unit(unit: str | None, has_weight: bool) -> str | None:
    if not unit:
        return "lb" if has_weight else None
    u = unit.lower()
    if u.startswith("pound") or u in {"lb", "lbs"}:
        return "lb"
    if u.startswith("kg"):
        return "kg"
    return u


def parse_exercise_data(raw: str) -> dict[str, Any] | None:
    d = re.sub(r"\s+", " ", raw or "").strip()
    if not d or d.lower().strip(" .") in EMPTY_DATA:
        return None

    m = re.match(
        r"^(?P<reps>[0-9,.\s]+)\s*reps?\s*x\s*(?P<wts>[0-9,.\s]*)\s*(?P<unit>pounds?|lbs?|kgs?)?\s*$",
        d,
        re.I,
    )
    if m and parse_num_list(m.group("reps")):
        reps = parse_num_list(m.group("reps"))
        wts = parse_num_list(m.group("wts") or "")
        return {
            "kind": "reps_weight" if wts else "reps_only",
            "reps": reps,
            "weights": wts,
            "unit": normalize_unit(m.group("unit"), bool(wts)),
            "raw": d,
        }

    m = re.match(
        r"^(?P<wts>[0-9,.\s]+)\s*(?P<unit>pounds?|lbs?|kgs?)\s*x\s*(?P<reps>[0-9,.\s]+)\s*reps?\s*$",
        d,
        re.I,
    )
    if m and parse_num_list(m.group("reps")):
        reps = parse_num_list(m.group("reps"))
        wts = parse_num_list(m.group("wts"))
        return {
            "kind": "reps_weight" if wts else "reps_only",
            "reps": reps,
            "weights": wts,
            "unit": normalize_unit(m.group("unit"), bool(wts)),
            "raw": d,
        }

    m = re.match(
        r"^(?P<times>[\d:,.\s]+)\s*(time|seconds?|min|minutes?)?\s*x\s*$",
        d,
        re.I,
    )
    if m and re.search(r"\d", m.group("times") or ""):
        times = [x.strip() for x in m.group("times").split(",") if x.strip()]
        return {"kind": "time", "times": times, "raw": d}

    return None


def session_date_of(row: dict[str, str]) -> date:
    raw = (row.get("RescheduledDate") or "").strip() or (row.get("ScheduledDate") or "").strip()
    return date.fromisoformat(raw)


def is_instructional(title: str) -> bool:
    t = title.strip().lower()
    if t in INSTRUCTIONAL_TITLES:
        return True
    if t.startswith("[example video]") or t.startswith("[view only]"):
        return True
    return False


def _is_tenx_pair(a: float, b: float) -> bool:
    return abs(a - b * 10) < 1e-6 or abs(b - a * 10) < 1e-6


def flag_typo_weights(weights: list[int | float | None]) -> list[bool]:
    """Flag the odd-one-out in a 10x typo pair (12.5 vs 125, 80 vs 8, etc.)."""
    flags = [False] * len(weights)
    nonzero = [(i, float(w)) for i, w in enumerate(weights) if w not in (None, 0)]
    if len(nonzero) < 2:
        return flags
    med = statistics.median([w for _, w in nonzero])
    for i, w in nonzero:
        partners = [other for j, other in nonzero if j != i and _is_tenx_pair(w, other)]
        if not partners:
            continue
        # Flag this value if it is farther from the median than a 10x partner.
        # On a tie (two-value 10x pair), flag the larger one — extra zeros are the usual typo.
        farther = False
        for other in partners:
            dw = abs(w - med)
            do = abs(other - med)
            if dw > do + 1e-9 or (abs(dw - do) <= 1e-9 and w > other):
                farther = True
                break
        if farther:
            flags[i] = True
    return flags


def epley_e1rm(weight: float, reps: float) -> float | None:
    if not weight or not reps or reps <= 0:
        return None
    if reps == 1:
        return float(weight)
    return round(weight * (1 + reps / 30.0), 1)


def clean_note(note: str) -> str | None:
    note = (note or "").strip()
    if not note:
        return None
    # Drop anything that looks like an email or phone number.
    if PII_EMAIL_RE.search(note) or PII_PHONE_RE.search(note):
        return "[note omitted: possible personal info]"
    return note


def expand_sets(parsed: dict[str, Any], typo_flags: list[bool] | None = None) -> list[dict[str, Any]]:
    sets: list[dict[str, Any]] = []
    if parsed["kind"] in {"reps_weight", "reps_only"}:
        reps = parsed.get("reps") or []
        wts = parsed.get("weights") or []
        n = max(len(reps), len(wts))
        flags = typo_flags or [False] * n
        for i in range(n):
            rep = reps[i] if i < len(reps) else (reps[-1] if reps else None)
            wt = wts[i] if i < len(wts) else (wts[-1] if wts else None)
            entry: dict[str, Any] = {
                "set": i + 1,
                "weight_lb": wt if parsed.get("unit") in (None, "lb") else wt,
                "unit": parsed.get("unit") if wt is not None else None,
                "reps": rep,
            }
            if parsed.get("unit") == "kg" and wt is not None:
                entry["weight_lb"] = round(float(wt) * 2.20462, 1)
                entry["weight_original"] = wt
                entry["unit"] = "kg"
            elif wt is not None:
                entry["unit"] = "lb"
            if i < len(flags) and flags[i]:
                entry["possible_typo"] = True
            sets.append(entry)
    elif parsed["kind"] == "time":
        for i, t in enumerate(parsed.get("times") or []):
            sets.append({"set": i + 1, "duration": t})
    return sets


def load_training_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_sessions(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    order: list[tuple[str, str, str]] = []
    for row in rows:
        key = (
            (row.get("WorkoutTitle") or "").strip(),
            (row.get("ScheduledDate") or "").strip(),
            (row.get("RescheduledDate") or "").strip(),
        )
        if key not in grouped:
            order.append(key)
        grouped[key].append(row)

    sessions: list[dict[str, Any]] = []
    for key in order:
        raw_rows = grouped[key]
        title, scheduled, rescheduled = key
        try:
            sdate = session_date_of(raw_rows[0])
        except ValueError:
            continue
        exercises: list[dict[str, Any]] = []
        for row in raw_rows:
            title_ex = (row.get("ExerciseTitle") or "").strip()
            if not title_ex or is_instructional(title_ex):
                continue
            parsed = parse_exercise_data(row.get("ExerciseData") or "")
            if not parsed:
                continue
            typo_flags = None
            if parsed["kind"] in {"reps_weight", "reps_only"}:
                typo_flags = flag_typo_weights(parsed.get("weights") or [])
            sets = expand_sets(parsed, typo_flags)
            if not sets:
                continue
            item: dict[str, Any] = {"name": title_ex, "sets": sets}
            note = clean_note(row.get("ExerciseNotes") or "")
            if note:
                item["notes"] = note
            exercises.append(item)
        if not exercises:
            continue
        session: dict[str, Any] = {
            "date": sdate.isoformat(),
            "scheduled_date": scheduled or None,
            "rescheduled_date": rescheduled or None,
            "title": title,
            "exercises": exercises,
        }
        sessions.append(session)
    sessions.sort(key=lambda s: (s["date"], s["title"]))
    return sessions


def iter_sets(sessions: list[dict[str, Any]]):
    for session in sessions:
        for ex in session["exercises"]:
            for st in ex["sets"]:
                yield session, ex, st


def entry_top_set(sets: list[dict[str, Any]]) -> dict[str, Any] | None:
    usable = [
        s
        for s in sets
        if not s.get("possible_typo") and s.get("weight_lb") not in (None,)
    ]
    if usable:
        return max(usable, key=lambda s: (float(s["weight_lb"]), s.get("reps") or 0))
    repped = [s for s in sets if s.get("reps") not in (None,)]
    if repped:
        return max(repped, key=lambda s: s.get("reps") or 0)
    return sets[-1] if sets else None


def exercise_entries(sessions: list[dict[str, Any]], names: list[str]) -> list[dict[str, Any]]:
    wanted = set(names)
    entries: list[dict[str, Any]] = []
    for session in sessions:
        for ex in session["exercises"]:
            if ex["name"] not in wanted:
                continue
            top = entry_top_set(ex["sets"])
            scheme = []
            for s in ex["sets"]:
                if s.get("possible_typo"):
                    scheme.append(f"{s.get('weight_lb')}x{s.get('reps')}?")
                elif s.get("weight_lb") is not None:
                    scheme.append(f"{s.get('weight_lb')}x{s.get('reps')}")
                elif s.get("reps") is not None:
                    scheme.append(f"x{s.get('reps')}")
                elif s.get("duration"):
                    scheme.append(str(s["duration"]))
            entries.append(
                {
                    "date": session["date"],
                    "workout": session["title"],
                    "exercise": ex["name"],
                    "sets": ex["sets"],
                    "notes": ex.get("notes"),
                    "top": top,
                    "scheme": ", ".join(scheme),
                    "top_weight": None if not top else top.get("weight_lb"),
                    "top_reps": None if not top else top.get("reps"),
                }
            )
    entries.sort(key=lambda e: (e["date"], e["exercise"]))
    return entries


def choose_working(entries: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str]:
    if not entries:
        return None, "no_history"
    weighted = [e for e in entries if e.get("top_weight") not in (None,)]
    if not weighted:
        return entries[-1], "reps_only"
    last = weighted[-1]
    prev = [e for e in weighted[:-1] if (e.get("top_weight") or 0) > 0][-5:]
    if prev and (last.get("top_weight") or 0) > 0:
        med = statistics.median([e["top_weight"] for e in prev])
        if med and last["top_weight"] < 0.5 * med:
            for e in reversed(weighted[:-1]):
                if (e.get("top_weight") or 0) >= 0.5 * med:
                    return e, "skipped_light_recent"
    return last, "latest"


def summarize_lift(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    chosen, reason = choose_working(entries)
    if not chosen:
        return None
    def to_pr(e):
        t = e.get("top") or {}
        if t.get("possible_typo") or t.get("weight_lb") in (None,):
            return None
        return {
            "date": e["date"],
            "workout": e["workout"],
            "exercise": e["exercise"],
            "weight_lb": t.get("weight_lb"),
            "reps": t.get("reps"),
            "scheme": e["scheme"],
        }

    def better(a, b):
        return b is None or (a["weight_lb"], a["reps"] or 0) > (b["weight_lb"], b["reps"] or 0)

    pr = None
    recent_pr = None
    recent_pr_cutoff = (date.today() - timedelta(days=548)).isoformat()
    for e in entries:
        cand = to_pr(e)
        if not cand:
            continue
        if better(cand, pr):
            pr = cand
        if e["date"] >= recent_pr_cutoff and better(cand, recent_pr):
            recent_pr = cand
    if recent_pr:
        if pr and (pr["date"], pr["weight_lb"], pr["reps"]) != (recent_pr["date"], recent_pr["weight_lb"], recent_pr["reps"]):
            # Keep the recent PR as the program default; stash all-time if older/heavier.
            all_time = pr
            pr = recent_pr
            pr = dict(pr)
            # attach after e1rm assignment via side field
            pr["_all_time_best"] = all_time
    out = {
        "source_exercise": chosen["exercise"],
        "source_date": chosen["date"],
        "source_workout": chosen["workout"],
        "weight_lb": chosen.get("top_weight"),
        "reps": chosen.get("top_reps"),
        "source_sets": chosen["scheme"],
        "selection": reason,
        "sessions_logged": len(entries),
        "first_logged": entries[0]["date"],
        "last_logged": entries[-1]["date"],
    }
    if chosen.get("notes"):
        out["source_notes"] = chosen["notes"]
    if reason == "skipped_light_recent":
        last = [e for e in entries if e.get("top_weight") not in (None,)][-1]
        out["more_recent_lighter_session"] = {
            "date": last["date"],
            "sets": last["scheme"],
            "exercise": last["exercise"],
        }
    if pr:
        all_time = pr.pop("_all_time_best", None) if isinstance(pr, dict) else None
        out["best_set"] = pr
        e1 = epley_e1rm(pr["weight_lb"], pr["reps"] or 0)
        if e1:
            out["best_set"]["e1rm_lb"] = e1
        if all_time:
            e1a = epley_e1rm(all_time["weight_lb"], all_time["reps"] or 0)
            if e1a:
                all_time["e1rm_lb"] = e1a
            out["all_time_best"] = all_time
    return out


def apply_working_weights(progress: dict[str, Any], sessions: list[dict[str, Any]], imported_on: date | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    weights = progress.setdefault("working_weights", {})
    for key, spec in EXERCISE_MAP.items():
        entry = weights.get(key)
        if not isinstance(entry, dict):
            continue
        # Prefer the first mapped candidate that has a log in the last 90 days.
        today = imported_on or date.today()
        recent_cutoff = (today - timedelta(days=90)).isoformat()
        related_cutoff = (today - timedelta(days=548)).isoformat()  # ~18 months
        stale_cutoff = (today - timedelta(days=90)).isoformat()

        chosen_name = None
        for name in spec["candidates"]:
            evs = exercise_entries(sessions, [name])
            if any(e["date"] >= recent_cutoff for e in evs):
                chosen_name = name
                break
        if chosen_name is None:
            for name in spec["candidates"]:
                evs = exercise_entries(sessions, [name])
                if any(e["date"] >= related_cutoff for e in evs):
                    chosen_name = name
                    break
        if chosen_name is None:
            all_cands = exercise_entries(sessions, spec["candidates"])
            if all_cands:
                chosen_name = all_cands[-1]["exercise"]

        use = exercise_entries(sessions, [chosen_name]) if chosen_name else []
        related_entries = [
            e
            for e in exercise_entries(sessions, spec.get("related") or [])
            if e["date"] >= related_cutoff
        ]
        summary = summarize_lift(use) if use else None

        # Clear previous import fields but keep original descriptive notes.
        for drop in (
            "source_exercise",
            "source_date",
            "source_workout",
            "source_sets",
            "selection",
            "related_lifts",
            "best_set",
            "more_recent_lighter_session",
        ):
            entry.pop(drop, None)

        if summary and summary.get("weight_lb") is not None:
            entry["weight_lb"] = summary["weight_lb"]
            entry["reps"] = summary["reps"]
            entry["unit"] = "lb"
            entry["source_exercise"] = summary["source_exercise"]
            entry["source_date"] = summary["source_date"]
            entry["source_workout"] = summary["source_workout"]
            entry["source_sets"] = summary["source_sets"]
            entry["selection"] = summary["selection"]
            extra_bits = []
            if summary["selection"] == "skipped_light_recent":
                light = summary.get("more_recent_lighter_session") or {}
                extra_bits.append(
                    f"Used this session instead of the lighter {light.get('date')} log ({light.get('sets')})."
                )
                entry["more_recent_lighter_session"] = light
            stale = summary["source_date"] < stale_cutoff
            if stale:
                extra_bits.append(
                    f"Last logged {summary['source_date']} — treat as a starting reference, not a current max. Re-establish in Week 1."
                )
            base_note = entry.get("notes") or ""
            # Keep the original instructional note, then append import provenance.
            provenance = (
                f"Imported from TrainHeroic: {summary['source_exercise']} on {summary['source_date']} "
                f"({summary['source_sets']})."
            )
            if extra_bits:
                provenance += " " + " ".join(extra_bits)
            if "Imported from TrainHeroic" in base_note:
                # replace prior import sentence(s) after a unique marker if re-run
                entry["notes"] = re.sub(
                    r"\s*Imported from TrainHeroic:.*$",
                    "",
                    base_note,
                ).rstrip()
                entry["notes"] = (entry["notes"] + " " + provenance).strip()
            else:
                entry["notes"] = (base_note + " " + provenance).strip()
            if summary.get("best_set"):
                entry["best_set"] = summary["best_set"]
                bs = summary["best_set"]
                records.append(
                    {
                        "program_key": key,
                        "exercise": bs["exercise"],
                        "weight_lb": bs["weight_lb"],
                        "reps": bs["reps"],
                        "date": bs["date"],
                        "workout": bs["workout"],
                        "e1rm_lb": bs.get("e1rm_lb"),
                        "source_sets": bs.get("scheme"),
                        "source": "trainheroic_import",
                    }
                )
            if summary.get("all_time_best"):
                entry["all_time_best"] = summary["all_time_best"]
                at = summary["all_time_best"]
                records.append(
                    {
                        "program_key": key,
                        "exercise": at["exercise"],
                        "weight_lb": at["weight_lb"],
                        "reps": at["reps"],
                        "date": at["date"],
                        "workout": at["workout"],
                        "e1rm_lb": at.get("e1rm_lb"),
                        "source_sets": at.get("scheme"),
                        "source": "trainheroic_import",
                        "role": "all_time",
                    }
                )
        elif summary and summary.get("reps") is not None:
            # Bodyweight / reps-only history (e.g. pull-ups)
            entry["weight_lb"] = 0 if "pull" in (summary["source_exercise"] or "").lower() else entry.get("weight_lb")
            entry["reps"] = summary["reps"]
            entry["source_exercise"] = summary["source_exercise"]
            entry["source_date"] = summary["source_date"]
            entry["source_workout"] = summary["source_workout"]
            entry["source_sets"] = summary["source_sets"]
            entry["selection"] = summary["selection"]
            provenance = (
                f"Imported from TrainHeroic: {summary['source_exercise']} on {summary['source_date']} "
                f"({summary['source_sets']}; no load logged, treated as bodyweight / reps-only)."
            )
            base_note = entry.get("notes") or ""
            if "Imported from TrainHeroic" in base_note:
                entry["notes"] = re.sub(r"\s*Imported from TrainHeroic:.*$", "", base_note).rstrip()
                entry["notes"] = (entry["notes"] + " " + provenance).strip()
            else:
                entry["notes"] = (base_note + " " + provenance).strip()

        related_summaries = []
        # Group related by exercise name, take latest of each
        by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for e in related_entries:
            by_name[e["exercise"]].append(e)
        for name, evs in by_name.items():
            rel = summarize_lift(evs)
            if not rel:
                continue
            related_summaries.append(
                {
                    "exercise": rel["source_exercise"],
                    "date": rel["source_date"],
                    "weight_lb": rel["weight_lb"],
                    "reps": rel["reps"],
                    "sets": rel["source_sets"],
                }
            )
            if rel.get("best_set") and rel["best_set"]["weight_lb"] not in (None,):
                bs = rel["best_set"]
                records.append(
                    {
                        "program_key": key,
                        "exercise": bs["exercise"],
                        "weight_lb": bs["weight_lb"],
                        "reps": bs["reps"],
                        "date": bs["date"],
                        "workout": bs["workout"],
                        "e1rm_lb": bs.get("e1rm_lb"),
                        "source_sets": bs.get("scheme"),
                        "source": "trainheroic_import",
                        "role": "related_variation",
                    }
                )
        if related_summaries:
            entry["related_lifts"] = related_summaries

        # If primary is empty but a related lift exists, leave weight_lb null
        # and point to the related lift in notes (do not invent a conversion).
        if entry.get("weight_lb") is None and related_summaries:
            latest_rel = max(related_summaries, key=lambda r: r["date"])
            provenance = (
                f"No direct history for this exact lift. Closest recent TrainHeroic variation: "
                f"{latest_rel['exercise']} on {latest_rel['date']} ({latest_rel['sets']}). "
                f"Do not convert this into a working weight — establish in Week 1."
            )
            base_note = entry.get("notes") or ""
            if "Imported from TrainHeroic" in base_note or "No direct history" in base_note:
                entry["notes"] = re.sub(
                    r"\s*(Imported from TrainHeroic:|No direct history for this exact lift\.).*$",
                    "",
                    base_note,
                ).rstrip()
                entry["notes"] = (entry["notes"] + " " + provenance).strip()
            else:
                entry["notes"] = (base_note + " " + provenance).strip()

        weights[key] = entry
    return records


def compact_completed(sessions: list[dict[str, Any]], since: date) -> list[dict[str, Any]]:
    out = []
    for session in sessions:
        if date.fromisoformat(session["date"]) < since:
            continue
        exercises = []
        for ex in session["exercises"]:
            sets = []
            for s in ex["sets"]:
                item = {k: v for k, v in s.items() if k != "unit" or v}
                sets.append(item)
            block = {"name": ex["name"], "sets": sets}
            if ex.get("notes"):
                block["notes"] = ex["notes"]
            exercises.append(block)
        out.append(
            {
                "date": session["date"],
                "session_name": session["title"],
                "source": "trainheroic_import",
                "log": f"logs/{session['date']}.md",
                "exercises": exercises,
            }
        )
    return out


def md_escape(text: str) -> str:
    return (text or "").replace("|", "\\|")


def write_daily_logs(log_dir: Path, sessions: list[dict[str, Any]], since: date, imported_on: str) -> list[Path]:
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for session in sessions:
        if date.fromisoformat(session["date"]) < since:
            continue
        by_date[session["date"]].append(session)

    written: list[Path] = []
    for day, day_sessions in by_date.items():
        path = log_dir / f"{day}.md"
        parts = [
            f"# Workout Log — {day}",
            "",
            f"- **Source:** TrainHeroic historical export (imported {imported_on}, America/Phoenix)",
            f"- **Date:** {day}",
        ]
        if len(day_sessions) == 1:
            s = day_sessions[0]
            parts.append(f"- **Day / session:** {s['title']}")
            parts.append(f"- **Scheduled date:** {s.get('scheduled_date') or 'n/a'}")
            parts.append(f"- **Rescheduled date:** {s.get('rescheduled_date') or 'n/a'}")
        else:
            titles = "; ".join(s["title"] for s in day_sessions)
            parts.append(f"- **Sessions this day:** {titles}")

        for s in day_sessions:
            heading = s["title"] if len(day_sessions) > 1 else None
            if heading:
                parts.extend(["", f"## {heading}"])
                parts.append(f"- **Scheduled date:** {s.get('scheduled_date') or 'n/a'}")
                parts.append(f"- **Rescheduled date:** {s.get('rescheduled_date') or 'n/a'}")
            parts.extend(["", "## Work sets" if not heading else "### Work sets", ""])
            for ex in s["exercises"]:
                parts.append(f"### {ex['name']}" if not heading else f"#### {ex['name']}")
                parts.append("")
                parts.append("| Set | Weight | Reps | Duration | Notes |")
                parts.append("| --- | --- | --- | --- | --- |")
                notes = md_escape(ex.get("notes") or "")
                for i, st in enumerate(ex["sets"]):
                    if st.get("possible_typo"):
                        wt = f"{st.get('weight_lb')} lb (possible typo)"
                    elif st.get("weight_lb") is not None:
                        unit = st.get("unit") or "lb"
                        wt = f"{st['weight_lb']} {unit}"
                    else:
                        wt = "—"
                    reps = st["reps"] if st.get("reps") is not None else "—"
                    dur = st.get("duration") or "—"
                    note_cell = notes if i == 0 else ""
                    parts.append(f"| {st.get('set', i+1)} | {wt} | {reps} | {dur} | {note_cell} |")
                parts.append("")
        parts.extend(
            [
                "## Logged by the bot",
                "",
                "- Imported from TrainHeroic historical workout export",
                "- Full history also stored in `history/trainheroic_history.json` and `history/trainheroic_history.csv`",
                "",
            ]
        )
        path.write_text("\n".join(parts), encoding="utf-8")
        written.append(path)
    return written


def write_history_json(path: Path, sessions: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    payload = {
        "source": "TrainHeroic athlete training-data export",
        "privacy_note": (
            "Contains workout history only: dates, session titles, exercises, "
            "sets, reps, weights, and training notes. No profile, contact, "
            "message, readiness, or nutrition data."
        ),
        **meta,
        "sessions": sessions,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_history_csv(path: Path, sessions: list[dict[str, Any]]) -> int:
    rows_out = []
    for session, ex, st in iter_sets(sessions):
        rows_out.append(
            {
                "date": session["date"],
                "scheduled_date": session.get("scheduled_date") or "",
                "rescheduled_date": session.get("rescheduled_date") or "",
                "workout_title": session["title"],
                "exercise": ex["name"],
                "set": st.get("set") or "",
                "weight_lb": st.get("weight_lb") if st.get("weight_lb") is not None else "",
                "reps": st.get("reps") if st.get("reps") is not None else "",
                "duration": st.get("duration") or "",
                "unit": st.get("unit") or "",
                "possible_typo": "yes" if st.get("possible_typo") else "",
                "notes": ex.get("notes") or "",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "scheduled_date",
                "rescheduled_date",
                "workout_title",
                "exercise",
                "set",
                "weight_lb",
                "reps",
                "duration",
                "unit",
                "possible_typo",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_out)
    return len(rows_out)


def count_stats(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    n_ex = 0
    n_sets = 0
    typo = 0
    dates = []
    for session, ex, st in iter_sets(sessions):
        n_sets += 1
        if st.get("set") == 1 or st.get("set") is None:
            n_ex += 1
        if st.get("possible_typo"):
            typo += 1
        dates.append(session["date"])
    # recount exercises properly
    n_ex = sum(len(s["exercises"]) for s in sessions)
    return {
        "sessions_imported": len(sessions),
        "exercise_entries_imported": n_ex,
        "sets_imported": n_sets,
        "possible_typos_flagged": typo,
        "date_range": {
            "first": min(dates) if dates else None,
            "last": max(dates) if dates else None,
        },
        "unique_dates": len({s["date"] for s in sessions}),
    }


def privacy_scan(root: Path) -> list[str]:
    hits: list[str] = []
    skip_dirs = {".git", "__pycache__"}
    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".json", ".csv", ".py", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if PII_EMAIL_RE.search(text):
            # allow the word 'email' in docs, but not addresses
            hits.append(f"email-like pattern in {path}")
        if PII_PHONE_RE.search(text):
            hits.append(f"phone-like pattern in {path}")
        # Skip the importer itself (it documents what it refuses to copy).
        if path.resolve() == Path(__file__).resolve():
            continue
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import TrainHeroic training_data.csv into this program.")
    parser.add_argument("--input", required=True, type=Path, help="Path to training_data.csv only")
    parser.add_argument("--program-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--recent-logs-since", default="2026-09-01", help="YYYY-MM-DD for markdown logs + completed_workouts")
    parser.add_argument("--imported-on", default=None, help="Override import date (YYYY-MM-DD)")
    args = parser.parse_args(argv)

    input_path = args.input.resolve()
    if input_path.name.lower() != "training_data.csv":
        print(
            "Refusing to read a file that is not named training_data.csv "
            "(privacy: only workout history may be imported).",
            file=sys.stderr,
        )
        return 2
    if not input_path.is_file():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2

    program_dir = args.program_dir.resolve()
    since = date.fromisoformat(args.recent_logs_since)
    imported_on = args.imported_on or date.today().isoformat()

    rows = load_training_rows(input_path)
    sessions = build_sessions(rows)
    if not sessions:
        print("No logged sessions found in training_data.csv", file=sys.stderr)
        return 1

    stats = count_stats(sessions)
    history_dir = program_dir / "history"
    log_dir = program_dir / "logs"
    history_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "imported_on": imported_on,
        "timezone": "America/Phoenix",
        "input_file": "training_data.csv",
        **stats,
    }
    write_history_json(history_dir / "trainheroic_history.json", sessions, meta)
    n_csv = write_history_csv(history_dir / "trainheroic_history.csv", sessions)
    written_logs = write_daily_logs(log_dir, sessions, since, imported_on)

    progress_path = program_dir / "progress.json"
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    records = apply_working_weights(progress, sessions, date.fromisoformat(imported_on))
    # Deduplicate PRs by exercise + date + weight + reps
    uniq = {}
    for rec in records:
        k = (rec.get("exercise"), rec.get("date"), rec.get("weight_lb"), rec.get("reps"))
        uniq[k] = rec
    progress["personal_records"] = sorted(
        uniq.values(),
        key=lambda r: (r.get("date") or "", r.get("exercise") or ""),
    )
    # Keep new-program completed_workouts to imported recent history only
    # (older sessions live in history/). Preserve any non-import entries.
    existing = [
        w
        for w in (progress.get("completed_workouts") or [])
        if w.get("source") != "trainheroic_import"
    ]
    progress["completed_workouts"] = existing + compact_completed(sessions, since)
    progress["trainheroic_import"] = {
        "imported_on": imported_on,
        "timezone": "America/Phoenix",
        "history_json": "history/trainheroic_history.json",
        "history_csv": "history/trainheroic_history.csv",
        "recent_logs_since": since.isoformat(),
        **stats,
        "note": (
            "Working weights and PRs come from logged TrainHeroic sets only. "
            "Lifts with no history were left empty. A more recent but much lighter "
            "session is noted and not used as the working weight."
        ),
    }
    notes = progress.get("notes") or ""
    import_sentence = (
        f" TrainHeroic history imported {imported_on} "
        f"({stats['sessions_imported']} logged sessions, "
        f"{stats['date_range']['first']} to {stats['date_range']['last']}). "
        "Use imported working weights as Week 1 starting references and adjust to the prescribed RPE."
    )
    notes = re.sub(r"\s*TrainHeroic history imported .*$", "", notes).rstrip()
    progress["notes"] = (notes + import_sentence).strip()
    progress_path.write_text(json.dumps(progress, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    hits = privacy_scan(program_dir)
    summary = {
        **stats,
        "csv_rows": n_csv,
        "markdown_logs_written": len(written_logs),
        "recent_logs_since": since.isoformat(),
        "personal_records": len(progress["personal_records"]),
        "privacy_hits": hits,
    }
    print(json.dumps(summary, indent=2))
    if hits:
        print("WARNING: privacy scan found possible personal data:", file=sys.stderr)
        for h in hits:
            print(" -", h, file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
