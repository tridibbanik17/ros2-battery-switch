"""
battery_node.py
--------------
A battery node that simulates a battery charge level.
Multiple instances can be launched with different node names and topic namespaces.

Each instance publishes a Float32 message to /<node_name>/status at 1 Hz.
The charge level randomly fluctuates to simulate a real battery.
"""

import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class BatteryNode(Node):
    def __init__(self):
        # Node name is set at launch time via remapping / --ros-args -r __node:=battery_1
        super().__init__('battery_node')

        # Declare a parameter for initial charge so each instance can differ
        self.declare_parameter('initial_charge', 100.0)
        self._charge = self.get_parameter('initial_charge').get_parameter_value().double_value

        # Publish on a topic named after this node instance, e.g. battery_1/status
        topic = f'{self.get_name()}/status'
        self._publisher = self.create_publisher(Float32, topic, 10)

        # Publish at 1 Hz
        self._timer = self.create_timer(1.0, self._publish_status)

        self.get_logger().info(
            f'Battery node "{self.get_name()}" started. '
            f'Publishing on "{topic}". Initial charge: {self._charge:.1f}%'
        )

    def _publish_status(self):
        # Simulate slow discharge with small random noise
        self._charge -= random.uniform(0.1, 0.5)
        self._charge = max(0.0, self._charge)  # clamp to 0

        msg = Float32()
        msg.data = round(self._charge, 2)
        self._publisher.publish(msg)

        self.get_logger().info(f'[{self.get_name()}] Charge: {msg.data:.2f}%')


def main(args=None):
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
