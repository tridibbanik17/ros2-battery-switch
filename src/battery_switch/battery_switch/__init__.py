"""
battery_switch — ROS 2 package for simulated battery switching.

This package provides two node types:

* **BatteryNode** — simulates a discharging battery and publishes its charge
  level on ``/<node_name>/status`` at 1 Hz.
* **UINode** — subscribes to exactly one battery's status topic at a time.
  The active battery can be switched at runtime via the ``active_battery``
  parameter.
"""
