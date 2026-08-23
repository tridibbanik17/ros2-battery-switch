"""
ui_node.py
----------
User Interface node that reads from one active battery at a time.

- Subscribes to the currently active battery's status topic.
- Exposes a ROS 2 parameter ``active_battery`` that controls which battery
  topic the node subscribes to.
- Only one battery subscription is active at any given moment.

Switching is triggered by setting the parameter at runtime::

    ros2 param set /ui_node active_battery battery_2
"""

import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import Float32


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_NODE_NAME: str = 'ui_node'
DEFAULT_ACTIVE_BATTERY: str = 'battery_1'
TOPIC_SUFFIX: str = 'status'
QUEUE_SIZE: int = 10


class UINode(Node):
    """Reads charge data from the currently active battery and logs it."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_NODE_NAME)

        # Parameter: which battery is currently active
        self.declare_parameter('active_battery', DEFAULT_ACTIVE_BATTERY)
        self._active_battery: str = (
            self.get_parameter('active_battery').get_parameter_value().string_value
        )

        # Current subscription handle (replaced on switch)
        self._subscription: Subscription | None = None
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

    def _build_topic_name(self, battery_name: str) -> str:
        """Construct the full topic path for a given battery name."""
        return f'{battery_name}/{TOPIC_SUFFIX}'

    def _subscribe_to(self, battery_name: str) -> None:
        """Destroy the old subscription and create a new one for *battery_name*."""
        if self._subscription is not None:
            self.destroy_subscription(self._subscription)
            self.get_logger().info(
                f'Unsubscribed from "{self._build_topic_name(self._active_battery)}"'
            )

        topic: str = self._build_topic_name(battery_name)
        self._subscription = self.create_subscription(
            Float32,
            topic,
            self._battery_callback,
            QUEUE_SIZE,
        )
        self._active_battery = battery_name
        self.get_logger().info(f'Now subscribed to "{topic}"')

    def _battery_callback(self, msg: Float32) -> None:
        """Called every time the active battery publishes a new reading."""
        self.get_logger().info(
            f'[UI] Active battery "{self._active_battery}" → charge: {msg.data:.2f}%'
        )

    # ------------------------------------------------------------------
    # Parameter change callback (the "switch" mechanism)
    # ------------------------------------------------------------------

    def _on_parameter_change(self, params: list) -> SetParametersResult:
        """React to runtime parameter updates — switch subscription if needed."""
        for param in params:
            if param.name == 'active_battery':
                new_battery: str = param.value
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


def main(args: list[str] | None = None) -> None:
    """Entry point for the ui_node executable."""
    # 1. Initialize rclpy
    rclpy.init(args=args)
    # 2. Instantiate the node
    node = UINode()
    try:
        # rclpy.spin(node) performs three key functions:
        # 1. Event Loop: Continuously checks for incoming middleware events.
        # 2. Callback Management: Routes events directly to user-defined functions like _battery_callback() or _on_parameter_change().
        # 3. Thread Blocking: Keeps script alive until shutdown or Ctrl+C.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 4. Clean up after spin exits (e.g., via Ctrl+C)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
          

if __name__ == '__main__':
    main()
