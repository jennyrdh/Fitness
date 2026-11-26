# Daily workout logs

One markdown file per day, named by date:

```
logs/YYYY-MM-DD.md
```

Use the local calendar date in **America/Phoenix**. Example: a Monday session on November 30, 2026 is `logs/2026-11-30.md`.

Create a file for every lifting day, Saturday cardio (even if skipped — note that it was skipped), and Sunday review. The bot should write or update the file after you report the session, and also append a structured entry to `completed_workouts` or `weekly_reviews` in `../progress.json`.

## Template

Copy this for each new log. Leave a dash or `n/a` rather than deleting a section.

```markdown
# Workout Log — YYYY-MM-DD

- **Week:** 1
- **Day / session:** Monday — Lower Body — Quad-Focused Strength
- **Date:** YYYY-MM-DD (America/Phoenix)
- **Start time / duration:**
- **Energy (1–5):**
- **Sleep quality (1–5):**
- **Stress (1–5):**
- **Body notes:** (soreness, pain, cycle, illness — only what you want tracked)

## Warm-Up / Prep

- [ ] Completed as prescribed
- Modifications:

## Work sets

Log every work set. Warm-up and ramp-up sets can be noted briefly under the lift if useful.

### A. [Primary lift]

| Set | Weight | Reps | RPE or RIR | Notes |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |

### B. [Secondary lift]

| Set | Weight | Reps | RPE or RIR | Notes |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |

### C / D / E. [Accessories and finisher]

Same table format. For supersets, label the pairing (for example C1 / C2) and log each movement separately. For unilateral work, log left and right, or note if sides were even.

## Substitutions

- Planned lift → what you did, and why

## How it felt

- What was strong
- What was hard or ugly
- Any pain or technique issues

## Cardio (Saturday only)

- Option chosen: Zone 2 / Intervals / Mixed / Skipped
- Mode (bike, walk, row, jog, other):
- Duration:
- Average effort or heart rate, if known:
- Notes:

## Weekly review (Sunday only)

- Sessions completed this week (Mon–Sat):
- Loads or reps that moved up:
- Lifts that stalled or felt off:
- Recovery (sleep, stress, soreness):
- Plan for next week (load changes, swaps, extra rest):

## Progression notes for next time

- Keep / add load / add reps / deload on:
- Working weights to update in `progress.json`:

## Logged by the bot

- `progress.json` updated: yes / no
- New or matched PRs:
- Follow-up question for next session:
```

## Field definitions

| Field | How to fill it |
| --- | --- |
| Weight | Working load in pounds, including the bar for barbell lifts. Use `BW` for bodyweight, and note added load if weighted (`BW+10`). |
| Reps | Completed clean reps. If you failed a rep, log the completed number and note the miss. |
| RPE or RIR | One is enough. RPE 8 = 2 RIR. If unsure, write both a number and a short comment (“maybe 1 left”). |
| Energy / sleep / stress | 1 is poor, 5 is great. These help explain a heavy or light day. |
| Unilateral work | If one side is clearly weaker, say which side and by how many reps or how much load. |

## Naming and updates

- If two sessions somehow share a date (for example a late makeup), keep one file and add a second session heading rather than creating a second file.
- If you correct a number later the same day, edit the file and also correct `progress.json`. Do not silently leave them out of sync.
- Missed lifting days still get a short file: session name, “missed,” and the reason (travel, illness, time). That keeps the weekly review honest.

## Historical TrainHeroic logs

Sessions imported from Jennifer's TrainHeroic export use the same `logs/YYYY-MM-DD.md` naming and a filled-in work-set table.

- Markdown logs are written for **logged sessions from 2026-09-01 onward** (her recent training block).
- The full history (2022-01-03 to 2026-11-26, 729 logged sessions) is in `../history/trainheroic_history.json` and `../history/trainheroic_history.csv`.
- Imported files are labeled `Source: TrainHeroic historical export`. They include only exercises that were actually logged (sets, reps, and/or weight). Training notes are kept; personal profile and message data are not.
- If a later session in this program falls on one of those dates, add a second session heading in the same file rather than replacing the imported history.
