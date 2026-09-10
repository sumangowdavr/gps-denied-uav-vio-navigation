import sys
from pathlib import Path
PKG = Path(__file__).resolve().parents[1] / 'gps_denied_uav'
sys.path.insert(0, str(PKG))
from gps_denied_uav.localization_monitor import LocalizationConfig, LocalizationMonitor

def test_fresh_pose_is_healthy():
    m = LocalizationMonitor(LocalizationConfig(max_pose_age_s=0.3, max_jump_m=1.0))
    assert m.update((0,0,0),10.0)
    assert m.healthy(10.1)

def test_stale_pose_is_unhealthy():
    m = LocalizationMonitor(LocalizationConfig(max_pose_age_s=0.3, max_jump_m=1.0))
    m.update((0,0,0),10.0)
    assert not m.healthy(10.5)
    assert m.last_reason == 'stale_pose'

def test_large_jump_is_rejected():
    m = LocalizationMonitor(LocalizationConfig(max_pose_age_s=1.0, max_jump_m=1.0))
    assert m.update((0,0,0),0.0)
    assert not m.update((2,0,0),0.1)
    assert not m.healthy(0.1)
