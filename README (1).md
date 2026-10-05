# ROS 2 Line-Sensing DC Motor Control (Assignment #02)

Actuators, Sensors and Signals – Fall 2026, KBTU

An Amperka Octoliner line sensor is read by an Arduino Uno and sent to ROS 2 over USB serial.
Two ROS 2 nodes decide whether the DC motor runs: **FORWARD** on a dark surface, **STOP** when
2 or more channels see white. The Arduino drives the motor through an L298N driver.

## Hardware
| Connection | Arduino / source |
|---|---|
| Octoliner VCC / GND / SDA / SCL | 5V / GND / A4 / A5 |
| L298N ENA / IN1 / IN2 | D9 (PWM, jumper removed) / D7 / D8 |
| L298N OUT1 / OUT2 | DC motor |
| L298N +12V / GND | Battery + / Battery − and Arduino GND |

## ROS 2 nodes
- `octoliner_serial_node` – serial bridge: publishes `/octoliner_data` (Int32MultiArray, 8 values), subscribes `/motor_command`
- `controller_node` – subscribes `/octoliner_data`, publishes `/motor_command` (String: FORWARD / STOP)

Parameters: `threshold` (600), `white_to_stop` (2), `port` (/dev/ttyACM0), `baud` (115200).

## Run (Ubuntu 24.04 / WSL2, ROS 2 Jazzy)
```bash
# Windows PowerShell (admin): share the Arduino with WSL2
usbipd attach --wsl --busid <BUSID>

# upload the sketch (once)
arduino-cli compile --fqbn arduino:avr:uno arduino/octo_ros
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno arduino/octo_ros

# terminal 1
python3 ros2_nodes/octoliner_serial_node.py
# terminal 2
python3 ros2_nodes/controller_node.py
# terminal 3
ros2 topic echo /octoliner_data
```
Requires `pip install pyserial`.
