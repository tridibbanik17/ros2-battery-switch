"""
battery_switch.launch.py
------------------------
Launches two battery node instances and one UI node.

Node graph::

    battery_1  (BatteryNode instance)  →  publishes /battery_1/status
    battery_2  (BatteryNode instance)  →  publishes /battery_2/status
    ui_node                            →  subscribes to one of the above at a time
"""

from launch import LaunchDescription
from launch_ros.actions import Node

# ---------------------------------------------------------------------------
# Launch configuration
# ---------------------------------------------------------------------------

PACKAGE_NAME: str = 'battery_switch'

BATTERY_CONFIGS: list[dict] = [
    {'name': 'battery_1', 'initial_charge': 90.0},
    {'name': 'battery_2', 'initial_charge': 60.0},
]

DEFAULT_ACTIVE_BATTERY: str = 'battery_1'


def _create_battery_node(config: dict) -> Node:
    """Create a battery node action from a configuration dict."""
    return Node(
        package=PACKAGE_NAME,
        executable='battery_node',
        name=config['name'],
        parameters=[{'initial_charge': config['initial_charge']}],
        output='screen',
    )


def generate_launch_description() -> LaunchDescription:
    """Build and return the launch description for the battery switch system."""
    battery_nodes = [_create_battery_node(cfg) for cfg in BATTERY_CONFIGS]

    ui_node = Node(
        package=PACKAGE_NAME,
        executable='ui_node',
        name='ui_node',
        parameters=[{'active_battery': DEFAULT_ACTIVE_BATTERY}],
        output='screen',
    )

    return LaunchDescription([*battery_nodes, ui_node])
