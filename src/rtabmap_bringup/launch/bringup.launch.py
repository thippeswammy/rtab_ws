from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """Generates the launch description for the RTAB-Map setup."""
    rtabmap_launch_dir = FindPackageShare('rtabmap_launch')
    
    return LaunchDescription([
        # --- Arguments ---
        # Pass through arguments to rtabmap.launch.py
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('qos', default_value='1', description='General QoS used for sensor input data'),
        DeclareLaunchArgument('rosbag_path', default_value='', description='Path to rosbag file to play (optional)'),
        DeclareLaunchArgument('bag_rate', default_value='1.0', description='Playback rate for rosbag'),
        
        # --- Static Transforms ---
        # Publish base_link -> velodyne
        # User specified: VLP is at base_link (or relative to it) with Pitch 14.25 degrees.
        # 14.25 degrees ~= 0.2487 radians
        # Archives x y z yaw pitch roll
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_velodyne',
            arguments=['--x', '0', '--y', '0', '--z', '0', '--yaw', '0', '--pitch', '0.2495', '--roll', '0', '--frame-id', 'base_link', '--child-frame-id', 'velodyne'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        
        # Publish velodyne -> camera_color_optical_frame
        # User specified: Camera is 20cm on top of VLP.
        # We assume "on top" means +Z in the Velodyne frame.
        # We also need the optical rotation for the camera (Z-forward).
        # Standard ROS optical frame: X-right, Y-down, Z-forward
        # Velodyne/Base frame: X-forward, Y-left, Z-up
        # Transform Velodyne -> Optical:
        # Yaw=-90 (to bring X to Y?), Pitch=0, Roll=-90 (to bring Z to X?)
        # Let's use a standard optical transform sequence:
        # 0 0 0.2 -1.57079632679 0 -1.57079632679
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='velodyne_to_camera',
            arguments=['--x', '0', '--y', '0', '--z', '0.1', '--yaw', '-1.57079632679', '--pitch', '0', '--roll', '-1.57079632679', '--frame-id', 'velodyne', '--child-frame-id', 'camera_color_optical_frame'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),

        # --- Point Cloud Filter ---
        # Remap input from bag (velodyne_points_ray) to filter input (points_raw)
        # Remap filter output (points_filtered) to what RTAB-Map expects (velodyne_points)
        Node(
            package='rtabmap_bringup',
            executable='velodyne_filter.py',
            name='velodyne_filter',
            parameters=[{'min_range': 0.25}, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            remappings=[
                ('points_raw', '/velodyne_points_ray'),
                ('points_filtered', '/velodyne_points')
            ]
        ),
        


        # --- RTAB-Map Launch ---
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([rtabmap_launch_dir, 'launch', 'rtabmap.launch.py'])
            ),
            launch_arguments={
                'rtabmap_args': "--delete_db_on_start --Vis/FeatureType 6 --Vis/CorNNType 3 --Vis/MinInliers 12 --Reg/Strategy 1 --RGBD/NeighborLinkRefining true --Grid/Sensor 2 --Icp/VoxelSize 0.1 --Mem/NotLinkedNodesKept true --Mem/IntermediateNodes true --Icp/RangeMin 0.25 --Grid/RangeMin 0.25",
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'rgb_topic': '/camera/color/image_raw',
                'depth_topic': '/camera/aligned_depth_to_color/image_raw',
                'camera_info_topic': '/camera/color/camera_info',
                'subscribe_scan_cloud': 'true',
                'scan_cloud_topic': '/velodyne_points', # Use raw topic
                'subscribe_scan': 'false', # Disable 2D scan subscription to avoid timestamp conflicts with delayed filtered cloud
                'scan_topic': '/scan_ignore', # Force ignore scan topic by remapping to dummy
                'odom_args': '--ros-args -p subscribe_scan:=false',
                'icp_odometry': 'true', # Enable ICP odometry
                'visual_odometry': 'false', # Disable Visual odometry
                # 'odom_topic': '/gnss/odometry/base_link', # Removed for on-board odometry
                'frame_id': 'base_link',
                'approx_sync': 'true',
                'wait_for_transform': '3.0', # Increased tolerance for bag playback
                'qos': LaunchConfiguration('qos'),
                'queue_size': '50',
                'sync_queue_size': '50',
                'topic_queue_size': '50',
                'odom_always_process_most_recent_frame': 'false', # Process all frames found in the bag
            }.items()
        ),

        # --- Rosbag Playback ---
        ExecuteProcess(
            condition=IfCondition(
                PythonExpression(['"', LaunchConfiguration('rosbag_path'), '" != ""'])
            ),
            cmd=['ros2', 'bag', 'play', LaunchConfiguration('rosbag_path'), '--clock', '--rate', LaunchConfiguration('bag_rate'), '--remap', '/velodyne_points:=/velodyne_points_ray'],
            output='screen'
        )
    ])
