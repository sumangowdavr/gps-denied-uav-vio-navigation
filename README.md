# GPS-Denied UAV Navigation with VIO (ROS 2)

A portfolio-oriented ROS 2 autonomy stack for GPS-denied multirotor navigation. The project is designed around an X500-class vehicle using visual-inertial odometry as the local pose source and a flight controller exposed through MAVROS-compatible topics/services.

> Scope note: this repository is intentionally independent of unpublished UAV target-tracking research. It focuses on localization health, waypoint navigation, failsafe behavior, and reproducible evaluation.

## Demo objective

The vehicle should:

1. take off without GPS,
2. consume VIO/local pose,
3. fly a waypoint mission,
4. detect degraded/stale localization,
5. hold safely during localization loss,
6. resume or abort according to configured policy,
7. log trajectory and localization-health metrics.

## Validation dashboard

Current software-level validation uses a deterministic closed-loop mission with an intentionally injected **3-second VIO dropout**. The controller detects localization loss, transitions to **HOLD**, sends zero velocity while localization is unavailable, then resumes navigation after localization recovers.

| Validation item | Result |
|---|---:|
| Unit tests | **10 / 10 passed** |
| Mission completion | **PASS** |
| Injected VIO dropout | **3.0 s** |
| Failsafe response | **HOLD** |
| Hold duration | **3.0 s** |
| Recovery after localization returns | **PASS** |
| Mission completion time | **25.4 s** |
| Final altitude | **2.00 m** |
| Final XY offset from home | **~0.116 m** |

### 3D mission behavior

![3D trajectory and failsafe](results/figures/trajectory_3d.svg)

The path visualization shows takeoff, waypoint traversal, and the location where the localization-loss failsafe is exercised.

### Mission state-machine response

![Mission state timeline](results/figures/mission_state_timeline.svg)

This timeline makes the safety behavior explicit: **TAKEOFF → NAVIGATE → HOLD → NAVIGATE → COMPLETE**.

### Closed-loop waypoint error distribution

![Waypoint error CDF](results/figures/error_cdf.svg)

The cumulative-error plot provides a distribution-level view rather than relying on only a single average error value.

### Original trajectory and dropout plots

![Synthetic mission trajectory](results/figures/trajectory_validation.svg)

![Waypoint error and VIO dropout](results/figures/error_dropout_validation.svg)

See [`docs/VALIDATION.md`](docs/VALIDATION.md) for test output, metrics, interpretation, and limitations.

> These plots are **software-level synthetic closed-loop validation**, not Gazebo/PX4 or hardware results. Simulator ground-truth vs VIO plots will replace/extend them in the next milestone.

## Architecture

```text
Camera + IMU
    |
    v
External VIO / SLAM
    |
    v
/vio/pose --------------------+
/vio/status                   |
                              v
                     Localization Monitor
                              |
                     /localization/health
                              |
                              v
Waypoint Mission ---> Mission Manager ---> Velocity Setpoint Controller
                                             |
                                             v
                                     /mavros/setpoint_velocity/cmd_vel
                                             |
                                             v
                                      PX4 / ArduPilot SITL
```

## ROS 2 package

`gps_denied_uav/` contains:

- `localization_monitor.py` — scores VIO freshness and jump consistency.
- `waypoint_controller.py` — pure control logic for position-to-velocity tracking.
- `mission_manager.py` — finite-state mission logic: WAIT_FOR_LOCALIZATION → TAKEOFF → NAVIGATE → HOLD/RECOVER → COMPLETE/ABORT.
- `mission_node.py` — ROS 2 node wiring pose, health, waypoint control, and velocity setpoints.
- `trajectory_logger.py` — CSV trajectory logging.
- `config/mission.yaml` — mission/failsafe parameters.
- `launch/gps_denied_mission.launch.py` — launch entry point.

## Evaluation

The repository includes tests and an experiment matrix for nominal missions, VIO dropouts, pose jumps, drift, and trajectory analysis. Simulation ground truth should be used to report VIO ATE/RMSE.

## Build

```bash
mkdir -p ~/gps_denied_ws/src
cd ~/gps_denied_ws/src
git clone https://github.com/sumangowdavr/gps-denied-uav-vio-navigation.git
cd ..
colcon build --symlink-install
source install/setup.bash
```

## Run tests

```bash
python3 -m pytest -q
```

Expected current result:

```text
..........                                                               [100%]
10 passed in 0.03s
```

## Run mission

```bash
ros2 launch gps_denied_uav gps_denied_mission.launch.py
```

## Safety

This is research and simulation code, not certified flight software. Validate frame conventions, flight-controller mode/arming interfaces, geofencing, watchdogs, and manual takeover in SITL/HITL before hardware use.
