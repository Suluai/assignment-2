# ESP32 + ROS 2: Line Sensor → DC Motor

Assignment #2 – Actuators, Sensors and Signals (KBTU, Fall 2026)

The Octoliner sensor detects where a black line is, and the motor reacts:
line on the right → forward, line on the left → reverse, farther from centre → faster, no line → stop.

## Components
ESP32 · Amperka Octoliner · ZK-5AD motor driver · JGB37-520 DC motor · 7.4–12 V battery · PC with ROS 2 Humble

## Wiring
| ESP32 | Connects to |
|---|---|
| 3V3, GND, GPIO21, GPIO22 | Octoliner VCC, GND, SDA, SCL |
| GPIO25, GPIO26 | ZK-5AD IN1, IN2 |
| GND | ZK-5AD GND (common ground) |

Motor → ZK-5AD MOTOA. Battery → ZK-5AD VCC/GND.

![Wiring](docs/wiring_diagram.png)

## ROS 2 nodes
- `esp32_node` (ESP32, micro-ROS) – publishes `/octoliner/raw`, subscribes `/cmd_vel`
- `line_sensor_subscriber` – **subscriber**: reads sensor data, publishes `/line/error`
- `motor_cmd_publisher` – **publisher**: sends motor speed on `/cmd_vel`

## Run
1. Upload `firmware/esp32_microros_node/esp32_microros_node.ino` to the ESP32
   (libraries: micro_ros_arduino (humble), Octoliner).
2. Build and start:
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch esp32_ros2_line_follower line_follower.launch.py port:=/dev/ttyUSB0
```
