import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('gps_denied_uav')
    params = os.path.join(share, 'config', 'mission.yaml')
    return LaunchDescription([
        Node(package='gps_denied_uav', executable='mission_node', name='gps_denied_mission', output='screen', parameters=[params]),
        Node(package='gps_denied_uav', executable='trajectory_logger', name='trajectory_logger', output='screen', parameters=[params]),
    ])
