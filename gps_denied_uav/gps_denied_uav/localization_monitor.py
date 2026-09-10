from dataclasses import dataclass
from math import sqrt
from typing import Optional, Tuple


@dataclass(frozen=True)
class LocalizationConfig:
    max_pose_age_s: float = 0.30
    max_jump_m: float = 1.50


class LocalizationMonitor:
    """Checks pose freshness and rejects implausibly large inter-sample jumps."""

    def __init__(self, config: LocalizationConfig):
        self.config = config
        self._last_position: Optional[Tuple[float, float, float]] = None
        self._last_stamp_s: Optional[float] = None
        self.last_reason = 'no_pose'

    def update(self, position, stamp_s: float):
        jump = 0.0
        if self._last_position is not None:
            jump = sqrt(sum((a - b) ** 2 for a, b in zip(position, self._last_position)))
        self._last_position = tuple(position)
        self._last_stamp_s = float(stamp_s)
        if jump > self.config.max_jump_m:
            self.last_reason = 'pose_jump'
            return False
        self.last_reason = 'ok'
        return True

    def healthy(self, now_s: float) -> bool:
        if self._last_stamp_s is None:
            self.last_reason = 'no_pose'
            return False
        if now_s - self._last_stamp_s > self.config.max_pose_age_s:
            self.last_reason = 'stale_pose'
            return False
        if self.last_reason == 'pose_jump':
            return False
        self.last_reason = 'ok'
        return True
