from reader import OculusReader
import rclpy
from rclpy.node import Node
import tf2_ros
from geometry_msgs.msg import TransformStamped
from scipy.spatial.transform import Rotation
import numpy as np


class OculusReaderNode(Node):
    def __init__(self):
        super().__init__('oculus_reader')
        self.oculus_reader = OculusReader()
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def publish_transform(self, transform, name):
        translation = transform[:3, 3]
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = name
        t.transform.translation.x = float(translation[0])
        t.transform.translation.y = float(translation[1])
        t.transform.translation.z = float(translation[2])

        # Extract quaternion from rotation matrix using scipy
        rotation_matrix = transform[:3, :3]
        quat = Rotation.from_matrix(rotation_matrix).as_quat()  # [x, y, z, w]
        t.transform.rotation.x = float(quat[0])
        t.transform.rotation.y = float(quat[1])
        t.transform.rotation.z = float(quat[2])
        t.transform.rotation.w = float(quat[3])

        self.tf_broadcaster.sendTransform(t)

    def timer_callback(self):
        transformations, buttons = self.oculus_reader.get_transformations_and_buttons()

        if 'r' not in transformations:
            return

        right_controller_pose = transformations['r']
        self.publish_transform(right_controller_pose, 'oculus')
        print('transformations', transformations)
        print('buttons', buttons)


def main(args=None):
    rclpy.init(args=args)
    node = OculusReaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()