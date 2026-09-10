# Integration guide

## Recommended simulation path

### Option A — PX4 SITL + Gazebo

Use an X500-class model with camera and IMU. Route an external VIO estimate into ROS 2 as `/vio/pose`, then feed the same estimate into the FCU vision/local-position interface required by your PX4 bridge.

### Option B — ArduPilot SITL + Gazebo

Use MAVROS for command and local pose integration, but verify the exact EKF external-navigation parameter set for your ArduPilot version before flight.

## Frames

This repository commands velocities in a ROS-style local map frame. Before real integration, explicitly verify:

- ROS ENU pose convention,
- FCU NED convention,
- bridge transforms,
- camera optical frame,
- body frame orientation.

A frame mismatch can create immediate unsafe motion.

## VIO dropout injection

For reproducible testing, place a relay node between the VIO estimator and `/vio/pose` and create scenarios such as:

1. nominal — no dropout,
2. 0.5 s dropout,
3. 2 s dropout,
4. dropout longer than `recovery_timeout_s`,
5. isolated 2 m pose jump,
6. slowly increasing drift.

The mission node should HOLD for recoverable cases and ABORT for prolonged failure.

## Ground truth evaluation

In simulation, log both:

- `/vio/pose`,
- simulator ground-truth pose.

Compute absolute trajectory error (ATE) after appropriate frame/time alignment. Do not claim VIO accuracy from mission position error alone.
