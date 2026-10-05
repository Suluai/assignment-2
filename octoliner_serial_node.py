#!/usr/bin/env python3
"""Node 1 - octoliner_serial_node (sensor / serial interface).

Publishes : /octoliner_data  (std_msgs/Int32MultiArray, 8 values)
Subscribes: /motor_command   (std_msgs/String, FORWARD / STOP)
"""
import time
import rclpy
import serial
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray, String


class OctolinerSerialNode(Node):
    def __init__(self):
        super().__init__('octoliner_serial_node')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baud', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value

        self.ser = serial.Serial(port, baud, timeout=0.05)
        time.sleep(2.0)  # Arduino resets when the port opens
        self.ser.reset_input_buffer()

        self.pub = self.create_publisher(Int32MultiArray, '/octoliner_data', 10)
        self.create_subscription(String, '/motor_command', self.on_command, 10)
        self.create_timer(0.02, self.poll_serial)
        self.get_logger().info(f'Serial node running on {port} @ {baud}')

    def on_command(self, msg):
        cmd = msg.data.strip().upper()
        if cmd in ('FORWARD', 'STOP'):
            self.ser.write((cmd + '\n').encode())

    def poll_serial(self):
        while self.ser.in_waiting:
            line = self.ser.readline().decode(errors='ignore').strip()
            parts = line.split(',')
            if len(parts) == 9 and parts[0] == 'S':
                try:
                    values = [int(x) for x in parts[1:]]
                except ValueError:
                    continue
                m = Int32MultiArray()
                m.data = values
                self.pub.publish(m)

    def destroy_node(self):
        try:
            self.ser.write(b'STOP\n')
            self.ser.close()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = OctolinerSerialNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
