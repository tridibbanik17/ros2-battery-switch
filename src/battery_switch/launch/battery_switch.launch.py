"""
battery_switch.launch.py
------------------------
Launches two battery node instances and one UI node.

Node graph:
  battery_1  (battery_node instance)  →  publishes on /battery_1/status
  battery_2  (battery_node instance)  →  publishes on /battery_2/status
  ui_node                             →  subscribes to one of the above at a time
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    battery_1 = Node(
        package='battery_switch',
        executable='battery_node',
        name='battery_1',           # sets the ROS node name → topic becomes battery_1/status
        parameters=[
            {'initial_charge': 90.0}   # battery 1 starts at 90%
        ],
        output='screen',
    )

    battery_2 = Node(
        package='battery_switch',
        executable='battery_node',
        name='battery_2',           # sets the ROS node name → topic becomes battery_2/status
        parameters=[
            {'initial_charge': 60.0}   # battery 2 starts at 60%
        ],
        output='screen',
    )

    ui = Node(
        package='battery_switch',
        executable='ui_node',
        name='ui_node',
        parameters=[
            {'active_battery': 'battery_1'}   # start reading from battery_1
        ],
        output='screen',
    )

    return LaunchDescription([battery_1, battery_2, ui])
