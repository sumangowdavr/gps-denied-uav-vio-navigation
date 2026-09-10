# Experiment matrix

| ID | Scenario | Purpose | Expected behavior |
|---|---|---|---|
| E1 | Nominal square mission | Baseline navigation | Complete mission |
| E2 | 0.5 s VIO dropout | Short interruption | Hold, recover, continue |
| E3 | 2 s VIO dropout | Moderate interruption | Hold, recover, continue |
| E4 | > recovery timeout | Localization failure | Hold then abort |
| E5 | Single large pose jump | Outlier rejection | Enter hold / reject update |
| E6 | Increasing VIO drift | Localization quality stress | Quantify truth-vs-VIO error |
| E7 | Faster waypoint mission | Control stress | Preserve bounded tracking error |
| E8 | Narrow obstacle environment | Integration stress | Later local-planner extension |

## Metrics

For each run record:

- success/failure,
- completion time,
- path length,
- per-waypoint error,
- VIO ATE/RMSE against simulator truth,
- maximum pose age,
- number of localization-health violations,
- total HOLD duration,
- recovery time,
- command saturation percentage.
