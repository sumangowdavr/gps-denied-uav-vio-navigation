from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'gps_denied_uav'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Suman Gowda',
    maintainer_email='maintainer@example.com',
    description='GPS-denied UAV waypoint navigation using external VIO localization.',
    license='MIT',
    entry_points={'console_scripts': [
        'mission_node = gps_denied_uav.mission_node:main',
        'trajectory_logger = gps_denied_uav.trajectory_logger:main',
    ]},
)
