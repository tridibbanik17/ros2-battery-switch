"""
ui_node.py
----------
User Interface node that reads from one active battery at a time.

- Subscribes to the currently active battery's status topic.
- Exposes a service /switch_battery that accepts a target battery name
  (e.g. "battery_1" or "battery_2") and switches the subscription.
- Only one battery subscription is active at any given moment.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from std_srvs.srv import SetBool

# We use a custom-ish approach: the service request carries the target battery name
# via a string. Since ROS 2 built-in services don't have a string request by default,
# we use the rcl_interfaces SetParametersAtomically or a simple workaround:
# we declare the target as a node parameter and use the std_srvs/Trigger pattern.
# For clarity we use rcl_interfaces/srv/SetParameters via parameter events,
# but the simplest approach for a beginner is to use a parameter + parameter event.
#
# SIMPLEST APPROACH: expose a ROS 2 parameter "active_battery" that the user
# can set via:  ros2 param set /ui_node active_battery battery_2
# The node watches for parameter changes and re-subscribes accordingly.
# This avoids defining a custom service interface for the first project.


class UINode(Node):
    def __init__(self):
        super().__init__('ui_node')

        # Parameter: which battery is currently active
        self.declare_parameter('active_battery', 'battery_1')
        self._active_battery = (
            self.get_parameter('active_battery').get_parameter_value().string_value
        )

        # Current subscription handle (we'll replace it on switch)
        self._subscription = None
        self._subscribe_to(self._active_battery)

        # Watch for parameter changes (this is how "switching" is triggered)
        self.add_on_set_parameters_callback(self._on_parameter_change)

        self.get_logger().info(
            f'UI node started. Currently reading from: "{self._active_battery}"'
        )
        self.get_logger().info(
            'To switch battery, run:\n'
            '  ros2 param set /ui_node active_battery battery_2\n'
            '  ros2 param set /ui_node active_battery battery_1'
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _subscribe_to(self, battery_name: str):
        """Destroy the old subscription and create a new one for battery_name."""
        # Destroy previous subscription if it exists
        if self._subscription is not None:
            self.destroy_subscription(self._subscription)
            self.get_logger().info(
                f'Unsubscribed from "{self._active_battery}/status"'
            )

        topic = f'{battery_name}/status'
        self._subscription = self.create_subscription(
            Float32,
            topic,
            self._battery_callback,
            10,
        )
        self._active_battery = battery_name
        self.get_logger().info(f'Now subscribed to "{topic}"')

    def _battery_callback(self, msg: Float32):
        """Called every time the active battery publishes a new reading."""
        self.get_logger().info(
            f'[UI] Active battery "{self._active_battery}" → charge: {msg.data:.2f}%'
        )

    # ------------------------------------------------------------------
    # Parameter change callback (the "switch" mechanism)
    # ------------------------------------------------------------------

    def _on_parameter_change(self, params):
        from rcl_interfaces.msg import SetParametersResult

        for param in params:
            if param.name == 'active_battery':
                new_battery = param.value
                if new_battery == self._active_battery:
                    self.get_logger().info(
                        f'Already reading from "{new_battery}", no change.'
                    )
                else:
                    self.get_logger().info(
                        f'Switching from "{self._active_battery}" to "{new_battery}"...'
                    )
                    self._subscribe_to(new_battery)

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = UINode()
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
