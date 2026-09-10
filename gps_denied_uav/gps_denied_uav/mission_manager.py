from dataclasses import dataclass
from enum import Enum, auto


class MissionState(Enum):
    WAIT_FOR_LOCALIZATION = auto()
    TAKEOFF = auto()
    NAVIGATE = auto()
    HOLD = auto()
    COMPLETE = auto()
    ABORT = auto()


@dataclass(frozen=True)
class MissionConfig:
    recovery_timeout_s: float = 5.0
    waypoint_hold_s: float = 0.75


class MissionManager:
    def __init__(self, config: MissionConfig):
        self.config = config
        self.state = MissionState.WAIT_FOR_LOCALIZATION
        self.waypoint_index = 0
        self._hold_started = None
        self._reached_started = None

    def step(self, now_s: float, localization_ok: bool, at_waypoint: bool, waypoint_count: int):
        if self.state in (MissionState.COMPLETE, MissionState.ABORT):
            return self.state

        if self.state == MissionState.WAIT_FOR_LOCALIZATION:
            if localization_ok:
                self.state = MissionState.TAKEOFF
            return self.state

        if not localization_ok:
            if self.state != MissionState.HOLD:
                self.state = MissionState.HOLD
                self._hold_started = now_s
            elif self._hold_started is not None and now_s - self._hold_started > self.config.recovery_timeout_s:
                self.state = MissionState.ABORT
            return self.state

        if self.state == MissionState.HOLD:
            self.state = MissionState.NAVIGATE if self.waypoint_index > 0 else MissionState.TAKEOFF
            self._hold_started = None

        if self.state in (MissionState.TAKEOFF, MissionState.NAVIGATE):
            if at_waypoint:
                if self._reached_started is None:
                    self._reached_started = now_s
                if now_s - self._reached_started >= self.config.waypoint_hold_s:
                    self.waypoint_index += 1
                    self._reached_started = None
                    if self.waypoint_index >= waypoint_count:
                        self.state = MissionState.COMPLETE
                    else:
                        self.state = MissionState.NAVIGATE
            else:
                self._reached_started = None

        return self.state
