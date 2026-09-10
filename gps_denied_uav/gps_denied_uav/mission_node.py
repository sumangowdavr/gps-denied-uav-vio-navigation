import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TwistStamped

from .localization_monitor import LocalizationConfig, LocalizationMonitor
from .mission_manager import MissionConfig, MissionManager, MissionState
from .waypoint_controller import ControllerConfig, WaypointController


class MissionNode(Node):
    def __init__(self):
        super().__init__('gps_denied_mission')
        self.declare_parameter('waypoints', [0.0,0.0,2.0, 3.0,0.0,2.0, 3.0,3.0,2.0, 0.0,3.0,2.0, 0.0,0.0,2.0])
        self.declare_parameter('kp_xy', 0.8)
        self.declare_parameter('kp_z', 0.8)
        self.declare_parameter('max_xy_speed', 1.0)
        self.declare_parameter('max_z_speed', 0.5)
        self.declare_parameter('position_tolerance', 0.20)
        self.declare_parameter('max_pose_age_s', 0.30)
        self.declare_parameter('max_jump_m', 1.50)
        self.declare_parameter('recovery_timeout_s', 5.0)
        self.declare_parameter('waypoint_hold_s', 0.75)
        self.declare_parameter('control_rate_hz', 20.0)

        flat = list(self.get_parameter('waypoints').value)
        if len(flat) % 3:
            raise ValueError('waypoints parameter must contain x,y,z triples')
        self.waypoints = [tuple(flat[i:i+3]) for i in range(0, len(flat), 3)]
        self.controller = WaypointController(ControllerConfig(
            kp_xy=float(self.get_parameter('kp_xy').value),
            kp_z=float(self.get_parameter('kp_z').value),
            max_xy_speed=float(self.get_parameter('max_xy_speed').value),
            max_z_speed=float(self.get_parameter('max_z_speed').value),
            position_tolerance=float(self.get_parameter('position_tolerance').value)))
        self.localization = LocalizationMonitor(LocalizationConfig(
            max_pose_age_s=float(self.get_parameter('max_pose_age_s').value),
            max_jump_m=float(self.get_parameter('max_jump_m').value)))
        self.manager = MissionManager(MissionConfig(
            recovery_timeout_s=float(self.get_parameter('recovery_timeout_s').value),
            waypoint_hold_s=float(self.get_parameter('waypoint_hold_s').value)))

        self.position = None
        self._last_state = None
        self.create_subscription(PoseStamped, '/vio/pose', self.pose_callback, 20)
        self.cmd_pub = self.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 20)
        self.create_timer(1.0 / float(self.get_parameter('control_rate_hz').value), self.control_step)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def pose_callback(self, msg):
        p = msg.pose.position
        self.position = (p.x, p.y, p.z)
        stamp_s = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.localization.update(self.position, stamp_s if stamp_s > 0 else self.now_s())

    def publish_velocity(self, vx=0.0, vy=0.0, vz=0.0):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.twist.linear.x, msg.twist.linear.y, msg.twist.linear.z = float(vx), float(vy), float(vz)
        self.cmd_pub.publish(msg)

    def control_step(self):
        if self.position is None or not self.waypoints:
            self.publish_velocity(); return
        now = self.now_s()
        healthy = self.localization.healthy(now)
        target = self.waypoints[min(self.manager.waypoint_index, len(self.waypoints)-1)]
        reached = self.controller.reached(self.position, target)
        state = self.manager.step(now, healthy, reached, len(self.waypoints))
        if state != self._last_state:
            self.get_logger().info(f'Mission state: {state.name} | localization={self.localization.last_reason}')
            self._last_state = state
        if state in (MissionState.WAIT_FOR_LOCALIZATION, MissionState.HOLD, MissionState.COMPLETE, MissionState.ABORT):
            self.publish_velocity(); return
        target = self.waypoints[min(self.manager.waypoint_index, len(self.waypoints)-1)]
        self.publish_velocity(*self.controller.velocity_command(self.position, target))


def main(args=None):
    rclpy.init(args=args)
    node = MissionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()


if __name__ == '__main__':
    main()
