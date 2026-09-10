# Validation Evidence

This document records the first reproducible validation milestone for the GPS-denied UAV navigation stack.

## 1. Unit tests

The pure-Python controller, localization monitor, and mission manager were tested with:

```bash
python3 -m pytest -q
```

Result:

```text
..........                                                               [100%]
10 passed in 0.03s
```

Validated behaviors include waypoint velocity generation, velocity saturation, localization freshness/jump checks, mission-state progression, HOLD behavior, recovery after localization restoration, and abort logic.

## 2. Closed-loop synthetic mission

A deterministic synthetic mission was executed using the same waypoint-control and mission concepts as the ROS 2 stack. The vehicle flew the default square-like waypoint mission at 2 m altitude.

A 3-second VIO outage was deliberately injected from 10.0 s to 13.0 s. During that window, velocity commands were forced to zero to represent the localization-loss HOLD policy. Once localization returned, navigation resumed automatically.

### Results

| Metric | Result |
|---|---:|
| Mission completed | Yes |
| Mission completion time | 25.4 s |
| Injected VIO dropout | 3.0 s |
| Time in HOLD | 3.0 s |
| Final X | 0.0045 m |
| Final Y | 0.1159 m |
| Final Z | 2.0000 m |
| Mean active-waypoint error | 1.080 m |
| Maximum active-waypoint error | 3.002 m |

The large waypoint-error peaks are expected because the metric is measured against the newly selected waypoint immediately after each waypoint transition; they do not represent localization error. Simulator ground-truth ATE/RMSE will be reported in the SITL/VIO phase.

## 3. Evidence figures

### Closed-loop XY trajectory

![Synthetic mission trajectory](../results/figures/trajectory_validation.svg)

The orange dashed path marks mission waypoints. The blue line is the closed-loop vehicle trajectory. The red marker indicates the location where the injected VIO outage caused the mission manager to hold.

### Waypoint error and injected localization loss

![Waypoint error and VIO dropout](../results/figures/error_dropout_validation.svg)

The shaded region marks the 3-second localization outage. The error remains constant during HOLD because the vehicle is intentionally commanded not to advance without a healthy localization source. Navigation resumes after localization is restored.

## Interpretation

This validation proves the software-level control and failsafe logic are internally consistent under a deterministic closed-loop test. It is **not yet proof of real VIO accuracy or real multirotor flight performance**. The next validation stage is PX4/ArduPilot SITL + Gazebo with simulator ground truth and an actual VIO estimator or realistic VIO proxy.

Planned next evidence:

- simulator ground truth vs VIO trajectory,
- ATE/RMSE and drift percentage,
- multiple dropout-duration trials,
- pose-jump rejection tests,
- recovery-time statistics,
- mission success rate across repeated runs,
- Gazebo screenshots and flight video/GIF.
