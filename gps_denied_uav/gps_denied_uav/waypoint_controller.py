from dataclasses import dataclass
from math import sqrt
from typing import Tuple


@dataclass(frozen=True)
class ControllerConfig:
    kp_xy: float = 0.8
    kp_z: float = 0.8
    max_xy_speed: float = 1.0
    max_z_speed: float = 0.5
    position_tolerance: float = 0.20


class WaypointController:
    def __init__(self, config: ControllerConfig):
        self.config = config

    def error(self, position, target) -> Tuple[float, float, float]:
        return (
            target[0] - position[0],
            target[1] - position[1],
            target[2] - position[2],
        )

    def distance(self, position, target) -> float:
        ex, ey, ez = self.error(position, target)
        return sqrt(ex * ex + ey * ey + ez * ez)

    def reached(self, position, target) -> bool:
        return self.distance(position, target) <= self.config.position_tolerance

    def velocity_command(self, position, target):
        ex, ey, ez = self.error(position, target)
        vx = self.config.kp_xy * ex
        vy = self.config.kp_xy * ey
        vz = self.config.kp_z * ez

        xy_norm = sqrt(vx * vx + vy * vy)
        if xy_norm > self.config.max_xy_speed and xy_norm > 0.0:
            scale = self.config.max_xy_speed / xy_norm
            vx *= scale
            vy *= scale

        vz = max(-self.config.max_z_speed, min(self.config.max_z_speed, vz))
        return vx, vy, vz
