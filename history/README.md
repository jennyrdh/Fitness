# TrainHeroic history

Jennifer Nixon's logged TrainHeroic workout history, imported on **2026-11-25** (America/Phoenix) from the official athlete `training_data.csv` export.

This folder is workout history only. The importer never reads or copies TrainHeroic profile, email, phone, chat, readiness survey, nutrition, or team files. Those stay out of this public repo.

## What's here

| File | Contents |
| --- | --- |
| `trainheroic_history.json` | Every logged session: date, session title, exercises, sets, reps, weights, and training notes |
| `trainheroic_history.csv` | The same history as one row per set, easy to filter or chart |

Prescribed sessions with no logged reps or weight were not imported. Instructional cards such as "How to Warm Up" were skipped. Likely 10x typos (for example `27.5` logged as `275`) are kept in the row and marked `possible_typo`.

## Coverage

- **Logged sessions:** 729
- **Exercise entries:** 4,120
- **Sets:** 10,032
- **Date range:** 2022-01-03 to 2026-11-26

Human-readable markdown logs for recent sessions (from 2026-09-01) live in `../logs/YYYY-MM-DD.md`. Working weights and PRs derived from this history live in `../progress.json`.

## Re-import

From the program root, pointing only at `training_data.csv`:

```bash
python scripts/import_trainheroic.py \
  --input /path/to/training_data.csv \
  --program-dir . \
  --recent-logs-since 2026-09-01
```
