# Battery Switch — ROS 2 Beginner Project

Two battery nodes publish charge readings. One UI node reads from whichever battery is currently active, and you can switch between them at runtime.

```
battery_1  →  /battery_1/status  ─┐
                                   ├─▶  ui_node  (reads one at a time)
battery_2  →  /battery_2/status  ─┘
```

---

## Prerequisites

### 1. ROS 2 (Jazzy)

```bash
# Verify your installation
printenv ROS_DISTRO
```

Should print `jazzy`. If not installed, follow the [official ROS 2 Jazzy install guide](https://docs.ros.org/en/jazzy/Installation.html).

### 2. colcon and rosdep

```bash
sudo apt update
sudo apt install python3-rosdep python3-colcon-common-extensions -y
```

---

## Build

```bash
# 1. Enter the workspace
cd battery_switch_ws

# 2. Source ROS 2
source /opt/ros/jazzy/setup.bash

# 3. Initialise rosdep (only needed once per machine)
sudo rosdep init
rosdep update

# 4. Install package dependencies
rosdep install --from-paths src --ignore-src -r -y

# 5. Build
colcon build

# 6. Source the workspace overlay
source install/setup.bash
```

---

## Run

```bash
ros2 launch battery_switch battery_switch.launch.py
```

You will see all three nodes printing to the screen:

- `battery_1` and `battery_2` each print their charge level every second.
- `ui_node` prints the reading it receives from the currently active battery.

By default the UI node reads from **battery_1**.

---

## Switch batteries at runtime

Open a **second terminal** and run:

```bash
# In the new terminal, enter the workspace
cd battery_switch_ws

# Load base ROS 2 framework
source /opt/ros/jazzy/setup.bash

# Load this workspace's packages
source install/setup.bash

# Switch to battery_2
ros2 param set /ui_node active_battery battery_2

# Switch back to battery_1
ros2 param set /ui_node active_battery battery_1
```

The UI node will immediately unsubscribe from the old battery and subscribe to the new one. You will see the change reflected in the first terminal's output.

---

## Inspect the system

These commands are useful for exploring what is running:

```bash
# List all active nodes
ros2 node list

# List all active topics
ros2 topic list

# Watch battery_1 directly (bypass the UI node)
ros2 topic echo /battery_1/status

# Watch battery_2 directly
ros2 topic echo /battery_2/status

# See all parameters of the UI node
ros2 param list /ui_node

# Check which battery is currently active
ros2 param get /ui_node active_battery
```

---

## Project structure

```
battery_switch_ws/
  src/
    battery_switch/
      battery_switch/
        battery_node.py       # Reusable battery node — launched as two instances
        ui_node.py            # UI node — subscribes to one battery at a time
      launch/
        battery_switch.launch.py  # Starts all 3 nodes in one command
      package.xml
      setup.py
      setup.cfg
```

---

## How the switch works

The UI node exposes a ROS 2 parameter called `active_battery`. When you call `ros2 param set`, the node's parameter callback fires, destroys the current subscription, and creates a new one pointing at the new battery's topic. No restart needed.

---

## ROS 2 concepts in this project

| Concept | Where it appears |
|---|---|
| Node | `BatteryNode`, `UINode` — one class, one responsibility |
| Multiple instances | `battery_1` and `battery_2` are both `battery_node` executables with different names |
| Topic | `/battery_1/status`, `/battery_2/status` carry `Float32` charge values |
| Publisher | `battery_node` publishes charge level at 1 Hz |
| Subscriber | `ui_node` subscribes and swaps the subscription on switch |
| Parameter | `active_battery` drives the switch; `initial_charge` sets per-instance start value |
| Launch file | Brings up all 3 nodes with a single command |

---

## Verified system behaviour

The following was observed after a full build and launch, confirming everything works as designed.

### 3 nodes, 2 topics

```bash
$ ros2 node list
/battery_1
/battery_2
/ui_node

$ ros2 topic list
/battery_1/status
/battery_2/status
/parameter_events
/rosout
```

- 3 nodes total: two instances of `battery_node` and one `ui_node`.
- Each battery node owns exactly one topic.
- `/parameter_events` and `/rosout` are standard ROS 2 system topics, always present.

### Switching batteries

```bash
$ ros2 param set /ui_node active_battery battery_1
Set parameter successful

$ ros2 param get /ui_node active_battery
String value is: battery_1
```

The UI node immediately unsubscribes from the previous battery and subscribes to the new one. No restart needed.

### UI node parameters

```bash
$ ros2 param list /ui_node
active_battery
start_type_description_service
use_sim_time
```

- `active_battery` — your custom parameter that controls which battery the UI node reads from.
- `use_sim_time` and `start_type_description_service` — standard ROS 2 built-ins, present on every node.

### Battery discharge to zero

When `ros2 topic echo /battery_1/status` or `/battery_2/status` shows `data: 0.0`, it means the battery has fully discharged. This is expected — the simulated charge decreases by a small random amount every second and clamps at 0. Relaunch the nodes to reset the charge to the initial values defined in the launch file.

### Full system summary

```
/battery_1  →  publishes /battery_1/status  (Float32, 1 Hz)
/battery_2  →  publishes /battery_2/status  (Float32, 1 Hz)
/ui_node    →  subscribes to exactly one of the above at a time
               controlled by the active_battery parameter
```
