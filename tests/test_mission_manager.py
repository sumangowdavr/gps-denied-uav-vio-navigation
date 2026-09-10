import sys
from pathlib import Path
PKG = Path(__file__).resolve().parents[1] / 'gps_denied_uav'
sys.path.insert(0, str(PKG))
from gps_denied_uav.mission_manager import MissionConfig, MissionManager, MissionState

def test_waits_for_localization_then_takeoff():
    m = MissionManager(MissionConfig())
    assert m.step(0.0, False, False, 2) == MissionState.WAIT_FOR_LOCALIZATION
    assert m.step(0.1, True, False, 2) == MissionState.TAKEOFF

def test_dropout_enters_hold_and_recovers():
    m = MissionManager(MissionConfig(recovery_timeout_s=5.0))
    m.step(0.0, True, False, 2)
    assert m.step(1.0, False, False, 2) == MissionState.HOLD
    assert m.step(2.0, True, False, 2) == MissionState.TAKEOFF

def test_prolonged_dropout_aborts():
    m = MissionManager(MissionConfig(recovery_timeout_s=2.0))
    m.step(0.0, True, False, 2)
    assert m.step(1.0, False, False, 2) == MissionState.HOLD
    assert m.step(3.1, False, False, 2) == MissionState.ABORT

def test_waypoint_progression_and_completion():
    m = MissionManager(MissionConfig(waypoint_hold_s=0.5))
    m.step(0.0, True, False, 2)
    assert m.step(1.0, True, True, 2) == MissionState.TAKEOFF
    assert m.step(1.6, True, True, 2) == MissionState.NAVIGATE
    assert m.waypoint_index == 1
    assert m.step(2.0, True, True, 2) == MissionState.NAVIGATE
    assert m.step(2.6, True, True, 2) == MissionState.COMPLETE
