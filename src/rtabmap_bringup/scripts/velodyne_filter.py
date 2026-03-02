#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np

class VelodyneFilter(Node):
    def __init__(self):
        super().__init__('velodyne_filter')
        
        self.declare_parameter('min_range', 0.5)
        self.min_range = self.get_parameter('min_range').value
        
        self.subscription = self.create_subscription(
            PointCloud2,
            'points_raw',
            self.listener_callback,
            10)
        self.publisher = self.create_publisher(PointCloud2, 'points_filtered', 10)
        self.get_logger().info(f'Velodyne Filter Node Started. Min Range: {self.min_range}m')

    def listener_callback(self, msg):
        # Convert PointCloud2 to numpy array
        # We cannot use pc2.read_points_numpy(msg) directly if fields have mixed types (throws AssertionError)
        # So we extract XYZ (float32) to calculate the mask, and apply it to the raw byte data.
        
        """Processes a PointCloud2 message and publishes a filtered version.
        
        This function converts a PointCloud2 message to a numpy array, extracting the
        x, y, and z coordinates while handling mixed field types. It calculates the
        squared distance of points from the origin and applies a mask to filter out
        points that are below a specified minimum range or are NaN. The filtered points
        are then used to create a new PointCloud2 message, which is published to the
        appropriate topic.
        
        Args:
            msg: The PointCloud2 message containing the point cloud data.
        """
        try:
            # Read x, y, z using generator (bypasses numpy type checks in read_points_numpy)
            # skip_nans=False to preserve 1:1 mapping with msg.data indices
            point_generator = pc2.read_points(msg, field_names=['x', 'y', 'z'], skip_nans=False)
            
            # Convert to numpy array (N, 3)
            # This is slightly less efficient than read_points_numpy but robust to mixed field types
            # Convert to numpy array
            # Removing dtype=np.float32 to allow structured array creation if input is structured
            xyz_array = np.array(list(point_generator))
            
            if xyz_array.size == 0:
                 # Handle empty clouds
                 return

            if xyz_array.dtype.names:
                x = xyz_array['x']
                y = xyz_array['y']
                z = xyz_array['z']
            else:
                x = xyz_array[:, 0]
                y = xyz_array[:, 1]
                z = xyz_array[:, 2]
            
        except ValueError as e:
            self.get_logger().warn(f'PointCloud2 message parsing error: {e}')
            return
        except Exception as e:
            self.get_logger().error(f'Unexpected error reading points: {e}')
            return

        # Calculate squared distance
        dist_sq = x**2 + y**2 + z**2
        min_dist_sq = self.min_range**2
        
        # Filter mask: Keep points >= min_range AND not NaN
        # (Assuming original intent of skip_nans=True in read_points_numpy was to remove NaNs)
        valid_mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        range_mask = dist_sq >= min_dist_sq
        mask = valid_mask & range_mask
        
        # Apply mask to original data
        # View raw data as array of records (bytes) of size point_step
        # Note: using uint8 view reshaped to (N, point_step)
        point_step = msg.point_step
        raw_data = np.frombuffer(msg.data, dtype=np.uint8)
        
        # Ensure data alignment
        if raw_data.size % point_step != 0:
            self.get_logger().error('PointCloud2 data size is not a multiple of point_step!')
            return
            
        points_view = raw_data.reshape(-1, point_step)
        
        # Filter
        filtered_points_view = points_view[mask]
        
        # Create new PointCloud2 message
        filtered_msg = PointCloud2()
        filtered_msg.header = msg.header
        filtered_msg.height = 1
        filtered_msg.width = filtered_points_view.shape[0]
        filtered_msg.fields = msg.fields
        filtered_msg.is_bigendian = msg.is_bigendian
        filtered_msg.point_step = msg.point_step
        filtered_msg.row_step = filtered_msg.width * filtered_msg.point_step
        filtered_msg.is_dense = True 
        filtered_msg.data = filtered_points_view.tobytes()
        
        self.publisher.publish(filtered_msg)

def main(args=None):
    rclpy.init(args=args)
    velodyne_filter = VelodyneFilter()
    rclpy.spin(velodyne_filter)
    velodyne_filter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
