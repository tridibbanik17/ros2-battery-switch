"""
battery_node.py
---------------
A battery simulator node that publishes charge level over time.

Multiple instances can be launched with different node names and topic namespaces.
Each instance publishes a Float32 message to /<node_name>/status at a configurable rate.
The charge level randomly fluctuates to simulate real battery discharge.
"""

import random

import rclpy
from rclpy.node import Node
from rclpy.timer import Timer
from rclpy.publisher import Publisher
from std_msgs.msg import Float32


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_NODE_NAME: str = 'battery_node'
DEFAULT_INITIAL_CHARGE: float = 100.0
PUBLISH_RATE_SEC: float = 1.0
DISCHARGE_MIN: float = 0.1
DISCHARGE_MAX: float = 0.5
CHARGE_FLOOR: float = 0.0
QUEUE_SIZE: int = 10


class BatteryNode(Node):
    """Simulates a battery that discharges over time and publishes its charge level."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_NODE_NAME)

        # Declare configurable initial charge parameter
        self.declare_parameter('initial_charge', DEFAULT_INITIAL_CHARGE)
        self._charge: float = (
            self.get_parameter('initial_charge').get_parameter_value().double_value
        )

        # Publish on a topic named after this node instance (e.g. battery_1/status)
        topic: str = f'{self.get_name()}/status'
        self._publisher: Publisher = self.create_publisher(Float32, topic, QUEUE_SIZE)

        # Periodic timer drives the publish cycle
        self._timer: Timer = self.create_timer(PUBLISH_RATE_SEC, self._publish_status)

        self.get_logger().info(
            f'Battery node "{self.get_name()}" started. '
            f'Publishing on "{topic}". Initial charge: {self._charge:.1f}%'
        )

    def _publish_status(self) -> None:
        """Simulate discharge and publish the current charge level."""
        self._charge -= random.uniform(DISCHARGE_MIN, DISCHARGE_MAX)
        self._charge = max(CHARGE_FLOOR, self._charge)

        msg = Float32()
        msg.data = round(self._charge, 2)
        self._publisher.publish(msg)

        self.get_logger().info(f'[{self.get_name()}] Charge: {msg.data:.2f}%')


def main(args: list[str] | None = None) -> None:
    """Entry point for the battery_node executable."""
    rclpy.init(args=args)
    node = BatteryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
