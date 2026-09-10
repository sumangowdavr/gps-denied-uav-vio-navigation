import sys
from pathlib import Path
PKG = Path(__file__).resolve().parents[1] / 'gps_denied_uav'
sys.path.insert(0, str(PKG))
from gps_denied_uav.waypoint_controller import ControllerConfig, WaypointController

def test_zero_at_target():
    c = WaypointController(ControllerConfig())
    assert c.velocity_command((1,2,3),(1,2,3)) == (0.0,0.0,0.0)
    assert c.reached((1,2,3),(1,2,3))

def test_xy_speed_is_saturated():
    c = WaypointController(ControllerConfig(kp_xy=10.0, max_xy_speed=1.0))
    vx,vy,_ = c.velocity_command((0,0,0),(10,10,0))
    assert abs((vx*vx+vy*vy)**0.5 - 1.0) < 1e-9

def test_vertical_speed_is_saturated():
    c = WaypointController(ControllerConfig(kp_z=5.0, max_z_speed=0.4))
    _,_,vz = c.velocity_command((0,0,0),(0,0,10))
    assert vz == 0.4
