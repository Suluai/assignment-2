#!/usr/bin/env python3
"""Node 2 - controller_node (motor command publisher).

Subscribes: /octoliner_data  (std_msgs/Int32MultiArray)
Publishes : /motor_command   (std_msgs/String, FORWARD / STOP)
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray, String


class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        self.declare_parameter('threshold', 600)     # <= threshold = WHITE
        self.declare_parameter('white_to_stop', 2)   # this many white -> STOP
        self.pub = self.create_publisher(String, '/motor_command', 10)
        self.create_subscription(Int32MultiArray, '/octoliner_data', self.on_data, 10)
        self.get_logger().info('Controller running')

    def on_data(self, msg):
        thr = self.get_parameter('threshold').value
        n = self.get_parameter('white_to_stop').value
        white = sum(1 for v in msg.data if v <= thr)
        cmd = 'STOP' if white >= n else 'FORWARD'
        out = String()
        out.data = cmd
        self.pub.publish(out)
        self.get_logger().info(f'{list(msg.data)}  white={white}  -> {cmd}')


def main():
    rclpy.init()
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
