# ESP32 + ROS Line Follower (Octoliner + ZK-5AD + JGB37-520)

Assignment #2 – *Actuators, Sensors and Signals*, Fall 2026, KBTU SITE.

An ESP32 reads an **Amperka Octoliner** 8-channel IR line sensor and drives two
**JGB37-520** DC gear motors through a **ZK-5AD** dual H-bridge. All decisions
are made in **ROS (Noetic)** on a PC; the ESP32 talks to ROS over USB using
**rosserial**.

![ROS graph](docs/ros_node_graph.png)

## ROS nodes & topics

| Node | Role | Subscribes | Publishes |
|---|---|---|---|
| `/esp32_serial` (ESP32 firmware) | hardware I/O | `/cmd_vel` | `/octoliner/raw` |
| `/line_sensor_subscriber` | **Subscriber node** – gets sensor data, computes line position | `/octoliner/raw` | `/line/error`, `/line/detected` |
| `/motor_cmd_publisher` | **Publisher node** – PD controller, sends commands to motors | `/line/error`, `/line/detected` | `/cmd_vel` |

`/cmd_vel` uses normalised values: `linear.x` ∈ [-1, 1] (forward speed),
`angular.z` ∈ [-1, 1] (+ = turn left). The ESP32 mixes them into left/right PWM
(0–255, 20 kHz). If no `/cmd_vel` arrives for 500 ms the motors stop.

## Wiring

![Wiring](docs/wiring_diagram.png)

| From | To | Note |
|---|---|---|
| ESP32 3V3 / GND | Octoliner VCC / GND | |
| ESP32 GPIO21 / GPIO22 | Octoliner SDA / SCL | I2C, address 42 (0x2A) |
| ESP32 GPIO25 / GPIO26 | ZK-5AD IN1 / IN2 | Motor A (left), PWM |
| ESP32 GPIO32 / GPIO33 | ZK-5AD IN3 / IN4 | Motor B (right), PWM |
| ZK-5AD MOTOA / MOTOB | Motor A / Motor B (M+ M−) | encoder wires unused |
| Battery + / − | ZK-5AD VCC / GND | 7.4–12 V (ZK-5AD max 14 V) |
| ESP32 GND | ZK-5AD GND | **common ground is required** |

> The ESP32 is powered from the PC's USB cable. Never feed the motor battery
> into the ESP32's 3V3 pin.

## Repository layout

```
esp32_ros_line_follower/
├── firmware/esp32_ros_node/esp32_ros_node.ino   # ESP32 code (rosserial)
├── scripts/line_sensor_subscriber.py            # ROS node 1
├── scripts/motor_cmd_publisher.py               # ROS node 2
├── launch/line_follower.launch                  # starts everything
├── docs/                                        # diagrams
├── package.xml, CMakeLists.txt                  # catkin package
└── README.md
```

## 1. Flash the ESP32

1. Arduino IDE → Boards Manager → install **esp32** (Espressif).
2. Library Manager → install **Rosserial Arduino Library** and **Octoliner** (Amperka).
   *Tip:* if `ros_lib` gives compile errors, regenerate it on the PC:
   `rosrun rosserial_arduino make_libraries.py ~/Arduino/libraries`
3. Open `firmware/esp32_ros_node/esp32_ros_node.ino`, select *ESP32 Dev Module*, upload.

## 2. Build the ROS package (Ubuntu 20.04 + ROS Noetic)

```bash
sudo apt install ros-noetic-rosserial ros-noetic-rosserial-python ros-noetic-rosserial-arduino
cd ~/catkin_ws/src
git clone https://github.com/<your-username>/esp32_ros_line_follower.git
cd ~/catkin_ws && catkin_make && source devel/setup.bash
sudo usermod -a -G dialout $USER     # serial permission (log out/in once)
```

## 3. Run

```bash
roslaunch esp32_ros_line_follower line_follower.launch port:=/dev/ttyUSB0
```

Useful checks:

```bash
rostopic echo /octoliner/raw      # 8 sensor values
rostopic echo /line/error         # -1 (left) .. +1 (right)
rqt_graph                         # node graph
rqt_plot /line/error /cmd_vel/angular/z
```

### Test the motors alone (no sensor logic)

```bash
rosrun rosserial_python serial_node.py _port:=/dev/ttyUSB0 _baud:=115200 &
rostopic pub -r 10 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.5}, angular: {z: 0.0}}'
```

## Tuning

| Parameter | Node | Default | Meaning |
|---|---|---|---|
| `line_is_dark` | subscriber | `true` | black line on white floor |
| `min_contrast` | subscriber | `80` | below this spread = "line lost" |
| `flip_direction` | subscriber | `false` | set `true` if the robot steers away from the line |
| `base_speed` | publisher | `0.45` | forward speed (0–1) |
| `kp`, `kd` | publisher | `0.6`, `0.15` | PD gains |

If a motor spins backwards, swap its two wires on the ZK-5AD terminal.

## License
MIT
