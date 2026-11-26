# Upper / Lower / Back Progressive Overload

A 4-week TrainHeroic-style strength and hypertrophy mesocycle for Jennifer Nixon.

Five lifting days (Monday–Friday), optional Saturday cardio, and Sunday rest, mobility, and weekly review. Lower-body training falls on Monday, Wednesday, and Friday, with distinct emphases so the three sessions can recover: a squat-strength day, a posterior-chain day, and a moderate full-lower and core day. Upper push (chest, shoulders, triceps) and back/pull are split across Tuesday and Thursday.

The program uses the same session shape common in TrainHeroic marketplace plans such as Rick Gorrell’s BUILT 5-day PPL + Upper/Lower, Jeremy Lezama’s 5D Hypertrophy/Strength, and Daniel Lemke’s 4-week RIR-wave blocks: a specific warm-up/prep, a primary lift with week-to-week overload, secondary and accessory supersets, and a short finisher or core.

This folder is the source of truth for daily workout notifications and progress tracking. It lives in [jennyrdh/Fitness](https://github.com/jennyrdh/Fitness).

## Weekly schedule

| Day | Session | Focus |
| --- | --- | --- |
| Monday | Lower Body — Quad-Focused Strength | Back squat primary, quad accessories, calves |
| Tuesday | Upper Body — Push, Shoulders & Arms | Bench press primary, incline and overhead press, triceps |
| Wednesday | Lower Body — Posterior Chain | RDL primary, hip thrust, hamstrings and glutes |
| Thursday | Back & Pull Focus | Row primary, chin-up or lat pulldown, upper back, rear delts, biceps |
| Friday | Lower Body — Full Lower & Core | Front squat primary, split squat, light hinge, core finisher |
| Saturday | Optional Cardio & Conditioning | Zone 2 steady state, or short intervals if recovered |
| Sunday | Rest / Mobility & Weekly Review | Easy mobility, walk if desired, review the week |

Workouts are written to take about 45–70 minutes. Saturday is optional by design. Sunday is a rest day, not a seventh training day. Friday is intentionally more moderate than Monday and Wednesday so squat and hinge strength can recover.

## How progression works

This is a 3+1 mesocycle: three building weeks, then a deload and realization week.

| Week | Intent | Primary lifts | Accessories / secondaries |
| --- | --- | --- | --- |
| 1 — Establish | Find honest working weights with clean technique | 4 work sets @ **RPE 7 (3 RIR)** | Start at the low-to-mid end of the rep range @ 2–3 RIR |
| 2 — Build | Add load or reps if Week 1 hit the target | Same prescription @ **RPE 8 (2 RIR)** | Add 1–2 reps per set if still inside the range |
| 3 — Overload | Highest productive week of the block | Slightly heavier or an extra set @ **RPE 8.5–9 (1–2 RIR)** | Push toward the top of the rep range |
| 4 — Deload + Realization | Cut fatigue, then set baselines for the next block | Volume cut ~40–50%, work sets @ **RPE 7**. Last working set of each primary may be an AMRAP stopped at **2–3 RIR** | 2 sets at the low end of the range @ RPE 7 |

Friday’s primary (front squat or goblet squat) stays in a slightly higher-rep strength-hypertrophy range even in Week 3, rather than jumping to a heavy 5 × 5, because it sits after Monday’s squat and Wednesday’s hinge.

**RPE / RIR quick scale:** RPE 7 = 3 reps in reserve, RPE 8 = 2 RIR, RPE 9 = 1 RIR, RPE 10 = no reps left. Rate the set by how many clean reps you had left, not by how hard the first reps felt.

**Primary-lift load jumps (Weeks 2–3):** If the previous week’s work sets landed at or easier than the target RPE with good form, add about **2.5–5 lb on upper-body barbell lifts** and **5–10 lb on lower-body barbell lifts**. If a set was harder than prescribed, keep the same load. Never chase a jump that breaks technique.

**Double progression (secondaries and accessories):** Stay in the written rep range at that week’s RIR. When *every* work set hits the top of the range at or under the target RIR, the next time you do that lift add the smallest plate (usually 2.5–5 lb, or the next dumbbell) and return to the bottom of the range.

**Week 4 AMRAPs** are not max tests. Stop with 2–3 reps in reserve. Those reps help estimate working weights for the next 4-week mesocycle.

**Stall rule:** If a lift is flat for two to three weeks despite good sleep and attendance, change one thing only — load, a close variation, or a small set adjustment — and note it in the log.

## How daily logging works

1. The daily workout routine reads `progress.json` (current week, current day, and working weights) and the matching session in `program.md`.
2. You get that day’s workout (warm-up, primary targets, accessories, finisher).
3. After you train, tell the bot what you actually did: loads, reps, RPE or RIR, substitutions, how it felt, and anything that hurt or felt off.
4. The bot updates:
   - `logs/YYYY-MM-DD.md` — a human-readable daily log (see `logs/README.md`)
   - `progress.json` — working weights, personal records, and a structured `completed_workouts` entry
   - `history/` — full TrainHeroic history already imported; new sessions stay in daily logs + `progress.json`
5. Those numbers drive the next session’s suggested loads using the progression rules above.
6. On Sunday, the weekly review looks at adherence, PRs, energy, and what to change next week. After Week 4, the review sets loads and any exercise swaps for the next mesocycle.

If `start_date` in `progress.json` is still `null`, the preferred start is the next Monday so the week lines up: **Monday, November 30, 2026 (America/Phoenix)**. If you want to begin sooner, use the coming days as a familiarization pass (Week 1 sessions at a conservative RPE 6–7), then start the official mesocycle that Monday.

## Files

| Path | Purpose |
| --- | --- |
| `program.md` | Full 4-week program, session by session |
| `progress.json` | Live state: week, day, working weights, PRs, completed logs, and TrainHeroic baselines |
| `logs/YYYY-MM-DD.md` | One markdown log per training or review day (recent TrainHeroic sessions from 2026-09-01 are already filled in) |
| `logs/README.md` | Daily log template and field definitions |
| `history/trainheroic_history.json` | Full logged TrainHeroic history (2022-01-03 to 2026-11-26) |
| `history/trainheroic_history.csv` | Same history, one row per set |
| `history/README.md` | What was imported and how to re-run the importer |
| `scripts/import_trainheroic.py` | Reusable importer: reads only `training_data.csv` and updates history, logs, and `progress.json` |


## TrainHeroic starting weights

Jennifer's official TrainHeroic export was imported on **2026-11-25** (America/Phoenix). **729 logged sessions** (4,120 exercise entries, 10,032 sets) from **2022-01-03 to 2026-11-26** are in `history/`. Only workout history was imported — no profile, contact, chat, readiness, or nutrition data.

The daily 7:00 AM and 4:00 PM routines should read working weights and PRs from `progress.json`. Those values are real logged sets, with the source exercise, date, and set list attached. Nothing was invented for a lift with no history.

Current baselines used for Week 1 (load still has to match the prescribed RPE):

| Program lift | Working weight | Taken from |
| --- | --- | --- |
| Back squat | 95 lb × 10 | Back Squat on 2025-05-29 (sparse / not current — re-establish; closest recent variation is Hack Squat 90 lb × 8 on 2026-04-30) |
| Leg press | 320 lb × 12 | Leg Press (glutes) on 2026-11-19 (the 2026-11-26 log was a lighter 90 lb × 12) |
| Leg extension | 115 lb × 8 | Leg Extensions on 2026-11-23 |
| Leg curl | 45 lb × 5 | SL Seated Ham Curl on 2026-11-26 (after 25×8, 40×5) |
| Standing calf raise | 150 lb × 15 | Standing Calf Raise Machine on 2026-11-23 |
| Barbell bench press | 65 lb × 5 | Flat BB Press on 2025-04-29 (not current — re-establish; recent horizontal push is Incline DB Press and Chest Press Machine) |
| Overhead press | 65 lb × 5 | Barbell Overhead Press on 2026-09-18 (recent variation: Shoulder press machine 25 lb × 10 on 2026-11-20) |
| Incline DB press | 30 lb × 12 (per DB) | Incline DB Press (60 degree) on 2026-11-24 |
| Lateral raise | 10 lb × 12 | SA behind the back lateral raise on 2026-11-20 |
| Overhead triceps extension | 30 lb × 12 | OH Tricep Ext (DB) on 2026-10-02 |
| Triceps pushdown | 31 lb × 9 | Tricep Pushdown on 2026-11-24 |
| Romanian deadlift | 135 lb × 6 | RDL on 2026-11-23 (after a 115×8) |
| Hip thrust | 270 lb × 10 | BB Hip Thrust on 2026-11-26 |
| Reverse lunge / step-up | 65 lb × 12 | FFE Reverse Lunge on 2026-11-23 |
| Back extension | 170 lb × 10 | 45 Degree hip extension on 2025-08-25 (re-establish if it feels stale) |
| Chest-supported / barbell row | 70 lb × 12 | Chest supported row machine (elbows flared) on 2026-11-24 |
| Chin-up / lat pulldown | 85 lb × 10 | Close Grip Pulldown on 2026-11-20 (recent pull-ups: bodyweight × 7 on 2026-09-11) |
| Single-arm row | 45 lb × 8 | SA DB Row on 2026-01-06 (re-establish) |
| Straight-arm pulldown / pullover | 27.5 lb × 10 | DB Pullovers on 2026-10-23 |
| Rear delt fly | 7.5 lb × 15 | Rear Delt Cable Fly on 2026-10-27 |
| EZ-bar / DB curl | 15 lb × 9 | Incline DB Curls on 2026-11-24 |
| Front / goblet squat | 45 lb × 12 | Goblet Squat on 2026-08-31 (no front squat history) |
| Bulgarian split squat | 35 lb × 12 | Bulgarian Split Squat on 2026-09-28 |
| Single-leg RDL | 35 lb × 8 | Single Leg RDL on 2026-09-03 |
| Seated calf raise | — | No direct history. Closest: Calf Raise (leg press) 160 lb × 22 on 2026-11-26. Establish in Week 1. |

Notable recent PRs (same lift, last ~18 months unless noted): hip thrust 270×10 (2026-11-26), RDL 165×5 (2026-04-06), incline DB press 35×9 (2026-09-01), barbell overhead press 65×7 (2026-09-11), chest-supported row 140×10 (2026-06-02), leg press 320×12 (2026-11-19; all-time 350×6 in 2022), goblet squat 50×12 (2026-05-28).

The new 5-day program still starts the official mesocycle on **Monday, November 30, 2026**. Until then, imported logs are historical context, not completed days of this mesocycle.

## Equipment and substitutions

Written for a standard gym: barbell and plates, squat rack, flat and incline bench, pull-up bar, dumbbells, cables, and common machines. If a movement is unavailable or uncomfortable, swap to the closest pattern and keep the same sets, reps, and RIR.

| Pattern | Main option | Solid swaps |
| --- | --- | --- |
| Horizontal push | Barbell bench press | Dumbbell bench, machine chest press |
| Vertical push | Dumbbell or barbell overhead press | Machine shoulder press, landmine press |
| Vertical pull | Chin-up / pull-up | Lat pulldown, band-assisted pull-up |
| Horizontal pull | Barbell or chest-supported row | Seated cable row, dumbbell row |
| Squat (Monday) | Back squat | Goblet squat, safety-bar or hack squat, squat-stance leg press |
| Front squat (Friday) | Front squat | Goblet squat, safety-bar squat, heels-elevated squat |
| Hip hinge | Romanian deadlift | Trap-bar RDL or deadlift, cable pull-through |
| Single-leg | Bulgarian split squat | Reverse lunge, step-up, walking lunge |
| Hip extension | Barbell hip thrust | Glute bridge, cable kickback, 45° back extension |

## Training guidelines

- Warm up as written, then take 2–4 ramp-up sets on the primary lift (for example empty bar, ~50%, ~70%, a heavy single or triple at ~90% of that day’s work weight) before the logged work sets.
- Accessories should use a controlled 2–3 second lowering phase and a smooth, not sloppy, lift.
- Rest periods are part of the program. Take the full rest on primaries.
- Stop a set if technique clearly breaks down, even if reps remain.
- Sharp joint pain is a stop-and-substitute signal, not something to train through. Muscle burn and last-rep effort are expected; pinching, stabbing, or unusual joint pain is not.
- This is general strength programming, not medical advice. If you have an injury or a health condition, get personal medical clearance before starting.
- Saturday cardio should be skipped or shortened if you are run down, badly sore from Friday, or short on sleep.
- Week 4 is a planned easier week. Do not turn it into another overload week.
- If a lower-body day leaves you unusually beat up, keep the next lower day’s primary at the previous week’s load and cut the last accessory pairing.

## After this mesocycle

When Week 4 is done, keep the same split, update working weights from the realization AMRAPs and logs, and start Mesocycle 2. Typical next-block changes: a slightly different primary variation (for example close-grip bench or a high-bar/low-bar squat swap), a small volume adjustment, or a stronger emphasis on a lagging lift. Do not jump straight into another overload week without the deload.
